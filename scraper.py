"""
Smartstore Review Scraper & Deterministic Filter Module
Collects public customer reviews from Naver Smartstore and filters high-quality reviews.
"""
import os
import re
import time
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def parse_smartstore_url(url: str) -> Dict[str, str]:
    """
    Parses a Naver Smartstore product URL to extract channel name and product ID.
    Supports standard, mobile, and brand store URLs:
    - https://smartstore.naver.com/{channel}/products/{id}
    - https://m.smartstore.naver.com/{channel}/products/{id}
    - https://brand.naver.com/{brand}/products/{id}
    """
    url = url.strip()
    pattern = r"https?://(?:m\.)?(?:smartstore|brand)\.naver\.com/([^/]+)/products/(\d+)"
    match = re.search(pattern, url)
    if match:
        return {
            "channel": match.group(1),
            "product_id": match.group(2),
            "normalized_url": f"https://smartstore.naver.com/{match.group(1)}/products/{match.group(2)}"
        }
    
    # Fallback pattern for raw product IDs
    id_match = re.search(r"/products/(\d+)", url)
    if id_match:
        return {
            "channel": "store",
            "product_id": id_match.group(1),
            "normalized_url": url
        }
    
    raise ValueError(f"유효한 네이버 스마트스토어 상품 URL이 아닙니다: {url}")


def extract_rating_from_text(text: str) -> int:
    """Extracts integer rating (1~5) from text or labels."""
    # Look for patterns like '평점 5', '5점', '★5', '5/5'
    match = re.search(r"[★\s]?([1-5])(?:\.0)?(?:\s*점|\s*/\s*5)?", text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return 5  # default rating


def scrape_smartstore_reviews(
    product_url: str,
    max_pages: int = 3,
    headless: bool = False,
    timeout_ms: int = 30000,
    progress_callback = None
) -> pd.DataFrame:
    """
    Scrapes customer reviews from a Naver Smartstore product page using Playwright.
    
    Args:
        product_url: The Naver Smartstore product page URL
        max_pages: Maximum number of review pagination pages to scrape
        headless: Whether to run browser in headless mode (headless=False is more reliable against Naver WAF)
        timeout_ms: Page timeout in milliseconds
        progress_callback: Optional callable(str, float) for reporting progress
    
    Returns:
        pd.DataFrame containing scraped reviews
    """
    from playwright.sync_api import sync_playwright

    url_info = parse_smartstore_url(product_url)
    target_url = url_info["normalized_url"]
    
    reviews: List[Dict[str, Any]] = []

    def report(msg: str, progress: float = 0.0):
        logger.info(msg)
        if progress_callback:
            progress_callback(msg, progress)

    report(f"스마트스토어 접속 준비: {target_url}", 0.1)

    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "naver_user_profile"))
    os.makedirs(profile_dir, exist_ok=True)

    with sync_playwright() as p:
        browser_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-dev-shm-usage",
        ]

        # Use standalone Chromium so it always pops up visibly without conflicting with existing Chrome tabs
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=headless,
            args=browser_args,
            viewport={"width": 1400, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ko-KR",
            slow_mo=100 if not headless else 0
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            report("상품 페이지 로딩 중...", 0.2)
            page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(2000)

            # Check if blocked, redirected to login, or error page
            title_text = page.title()
            current_url = page.url
            body_text = page.locator("body").inner_text()

            # If error page with reload button, try clicking reload once
            if "에러페이지" in title_text or "시스템오류" in title_text:
                reload_btn = page.locator("a:has-text('새로고침')")
                if reload_btn.count() > 0 and reload_btn.is_visible():
                    report("페이지 새로고침 시도 중...", 0.22)
                    reload_btn.click()
                    page.wait_for_timeout(2500)
                    title_text = page.title()
                    current_url = page.url
                    body_text = page.locator("body").inner_text()

            # If redirected to login page and running in visible browser mode
            if "nidlogin" in current_url or "nid.naver.com" in current_url:
                if not headless:
                    report("🔑 네이버 로그인이 필요한 상품입니다. 화면의 브라우저 창에서 로그인해주세요 (최대 45초 대기 중)...", 0.25)
                    # Wait up to 45 seconds for user to log in
                    start_wait = time.time()
                    while time.time() - start_wait < 45:
                        if "nidlogin" not in page.url and "nid.naver.com" not in page.url:
                            report("로그인 성공! 상품 페이지로 이동 중...", 0.3)
                            page.wait_for_timeout(3000)
                            title_text = page.title()
                            current_url = page.url
                            body_text = page.locator("body").inner_text()
                            break
                        time.sleep(1.5)
                
                if "nidlogin" in page.url or "nid.naver.com" in page.url:
                    raise RuntimeError(
                        "해당 스마트스토어 상품은 네이버 로그인이 필수인 상품/스토어입니다.\n"
                        "열린 브라우저 창에서 네이버 로그인을 완료하시거나, "
                        "브라우저의 리뷰 텍스트를 복사하여 '리뷰 직접 붙여넣기' 또는 'CSV 파일 업로드' 기능을 이용해주세요."
                    )

            if (
                "에러페이지" in title_text 
                or "시스템오류" in title_text 
                or "접속이 불가" in body_text 
                or "일시적으로 이용이 불가능" in body_text
            ):
                raise RuntimeError(
                    f"네이버에서 상품 페이지를 불러오지 못했습니다 (페이지 제목: {title_text}).\n\n"
                    "🔍 주요 원인:\n"
                    "1. 해당 상품이 비공개/성인인증/로그인 전용 스토어입니다. (일반 브라우저에서는 로그인되어 있어 보이지만 자동화 창은 비로그인 상태)\n"
                    "2. 네이버 자동화 탐지(WAF)로 인해 비로그인 접근이 제한되었습니다.\n\n"
                    "💡 즉시 해결 방법:\n"
                    "- 사용 중이신 일반 브라우저에서 리뷰 텍스트를 복사하여 대시보드의 '리뷰 직접 붙여넣기' 또는 'CSV 업로드'에 넣으시면 차단 없이 즉시 100% 동일한 AI 분석이 가능합니다."
                )

            # Progressive scroll to trigger lazy-loaded review preview and find '리뷰 전체보기'
            report("리뷰 섹션 탐색 및 '리뷰 전체보기' 버튼 찾는 중...", 0.3)
            found_btn = None
            for scroll_y in [600, 1200, 1800, 2400, 3200]:
                page.evaluate(f"window.scrollTo(0, {scroll_y})")
                page.wait_for_timeout(600)

                btn_candidates = [
                    page.locator("button, a").filter(has_text=re.compile(r"리뷰\s*전체보기")),
                    page.locator("button:has-text('리뷰 전체보기'), a:has-text('리뷰 전체보기')"),
                    page.locator(":text('리뷰 전체보기')"),
                    page.locator("#REVIEW").get_by_role("button", name=re.compile(r"리뷰\s*전체보기")),
                    page.locator("a[href*='review'], button[class*='review']").filter(has_text="전체보기"),
                ]
                for candidate in btn_candidates:
                    if candidate.count() > 0:
                        for idx in range(candidate.count()):
                            el = candidate.nth(idx)
                            if el.is_visible():
                                found_btn = el
                                break
                    if found_btn:
                        break
                if found_btn:
                    break

            if found_btn:
                report("'리뷰 전체보기' 버튼 발견! 리뷰 모달 창을 여는 중...", 0.35)
                try:
                    found_btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    found_btn.click()
                    page.wait_for_timeout(2500)
                except Exception as click_err:
                    logger.info(f"일반 클릭 실패, JavaScript 강제 클릭 시도: {click_err}")
                    try:
                        found_btn.evaluate("el => el.click()")
                        page.wait_for_timeout(2500)
                    except:
                        pass
            else:
                report("본문 리뷰 목록 직접 탐색 중...", 0.35)

            # Check if modal container opened and scroll inside modal if needed
            modal_elem = page.locator("div[class*='modal'], div[role='dialog'], div[class*='layer_wrap'], div[class*='drawer']").first
            is_modal = modal_elem.count() > 0 and modal_elem.is_visible()
            if is_modal:
                report("리뷰 모달 창 로드 완료! 리뷰 데이터 수집 시작...", 0.38)
            else:
                report("리뷰 데이터 수집 시작...", 0.38)

            # Collect reviews page by page
            current_page = 1
            while current_page <= max_pages:
                report(f"리뷰 {current_page}페이지 수집 중...", 0.4 + (current_page / max_pages) * 0.5)
                
                # Expand any '더보기' text buttons in reviews
                try:
                    expand_buttons = page.locator("button:has-text('더보기'), a:has-text('더보기')").all()
                    for btn in expand_buttons[:10]:
                        if btn.is_visible():
                            try:
                                btn.click(timeout=1000)
                            except:
                                pass
                except:
                    pass

                # If inside modal, scroll modal content to render review items
                try:
                    modal_scrollable = page.locator("div[role='dialog'], div[class*='modal'], div[class*='drawer'], div[class*='layer_wrap']").first
                    if modal_scrollable.count() > 0:
                        modal_scrollable.evaluate("el => el.scrollBy(0, 1000)")
                        page.wait_for_timeout(800)
                except:
                    pass

                # Locate review items with extensive fallback selectors
                review_locators = page.locator("li[id^='REVIEW_ITEM_']").all()
                if not review_locators:
                    review_locators = page.locator("div[class*='reviewItems_review_item']").all()
                if not review_locators:
                    review_locators = page.locator("ul[class*='review_list'] > li, ul[class*='ReviewList'] > li").all()
                if not review_locators:
                    review_locators = page.locator("div[class*='ReviewItem'], li[class*='ReviewItem'], div[class*='review_item']").all()
                if not review_locators:
                    # Generic review cards
                    review_locators = page.locator("div[role='dialog'] li, div[class*='modal'] li").all()

                logger.info(f"{current_page}페이지에서 {len(review_locators)}개 리뷰 발견")

                for idx, item in enumerate(review_locators):
                    try:
                        full_text = item.inner_text().strip()
                        if not full_text:
                            continue

                        # Extract review id
                        item_id = item.get_attribute("id") or f"rev_p{current_page}_{idx+1}"

                        # Extract rating
                        rating_elem = item.locator("em[class*='rating'], span[class*='grade'], span[class*='score']").first
                        rating_val = 5
                        if rating_elem.count() > 0:
                            rating_val = extract_rating_from_text(rating_elem.inner_text())
                        else:
                            rating_val = extract_rating_from_text(full_text[:40])

                        # Extract user ID
                        user_elem = item.locator("strong[class*='name'], span[class*='user'], span[class*='writer']").first
                        user_id = user_elem.inner_text().strip() if user_elem.count() > 0 else f"user_{idx+1}"

                        # Extract date
                        date_match = re.search(r"(\d{2,4}\.\d{2}\.\d{2})", full_text)
                        created_date = date_match.group(1) if date_match else ""

                        # Extract options
                        option_elem = item.locator("div[class*='option'], span[class*='option']").first
                        option_name = option_elem.inner_text().strip() if option_elem.count() > 0 else ""

                        # Extract photo URLs
                        images = item.locator("img").all()
                        photo_urls = []
                        for img in images:
                            src = img.get_attribute("src") or img.get_attribute("data-src") or ""
                            if src and ("phinf" in src or "naver" in src or "upload" in src):
                                # Filter out profile icons / badges
                                if "profile" not in src.lower() and "badge" not in src.lower() and "icon" not in src.lower():
                                    photo_urls.append(src)

                        # Clean review content text: remove user name, date, options headers
                        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
                        # Filter out known header lines
                        content_lines = []
                        for line in lines:
                            if line.startswith("평점") or line.startswith("신고") or line.startswith("BEST"):
                                continue
                            if line == user_id or line == created_date or line == option_name:
                                continue
                            if line in ["더보기", "접기", "도움돼요", "답글", "사진/동영상"]:
                                continue
                            content_lines.append(line)

                        clean_content = " ".join(content_lines)
                        if len(clean_content) < 5:
                            clean_content = full_text

                        reviews.append({
                            "review_id": item_id,
                            "user_id": user_id,
                            "rating": rating_val,
                            "created_date": created_date,
                            "option_name": option_name,
                            "review_text": clean_content,
                            "photo_urls": photo_urls,
                            "image_count": len(photo_urls),
                        })
                    except Exception as item_err:
                        logger.debug(f"개별 리뷰 파싱 에러: {item_err}")

                if current_page >= max_pages:
                    break

                # Pagination: try to click next page button
                next_page_clicked = False
                next_btn = page.locator(f"a:has-text('{current_page + 1}'), button:has-text('{current_page + 1}')").first
                if next_btn.count() > 0 and next_btn.is_visible():
                    next_btn.click()
                    page.wait_for_timeout(2000)
                    next_page_clicked = True
                else:
                    # Try clicking the next '>' pagination arrow
                    next_arrow = page.locator("a[class*='next'], button[class*='next'], a[aria-label='다음']").first
                    if next_arrow.count() > 0 and next_arrow.is_visible():
                        next_arrow.click()
                        page.wait_for_timeout(2000)
                        next_page_clicked = True

                if not next_page_clicked:
                    logger.info("더 이상 다음 페이지 버튼이 없습니다.")
                    break

                current_page += 1

            report(f"스크래핑 완료! 총 {len(reviews)}개의 리뷰를 수집했습니다.", 1.0)

        finally:
            try:
                if context:
                    context.close()
            except:
                pass

    df = pd.DataFrame(reviews)
    if not df.empty:
        df["text_length"] = df["review_text"].apply(lambda x: len(str(x)))
    return df


def load_reviews_from_file(file_or_path) -> pd.DataFrame:
    """
    Loads customer reviews from an Excel (.xlsx, .xls) or CSV file/buffer.
    Intelligently maps various column names from Smartstore scrapers and extensions
    to standard schema: review_id, user_id, rating, created_date, option_name,
    review_text, photo_urls, image_count, text_length.
    """
    filename = ""
    if hasattr(file_or_path, "name"):
        filename = getattr(file_or_path, "name", "").lower()
    elif isinstance(file_or_path, str):
        filename = file_or_path.lower()

    df = None
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        try:
            df = pd.read_excel(file_or_path)
        except Exception as e:
            logger.warning(f"Failed to read as Excel: {e}")

    if df is None:
        try:
            # Try reading as CSV with utf-8 first
            df = pd.read_csv(file_or_path, encoding="utf-8")
        except (UnicodeDecodeError, Exception):
            try:
                if hasattr(file_or_path, "seek"):
                    file_or_path.seek(0)
                df = pd.read_csv(file_or_path, encoding="cp949")
            except Exception:
                try:
                    if hasattr(file_or_path, "seek"):
                        file_or_path.seek(0)
                    df = pd.read_csv(file_or_path, encoding="euc-kr")
                except Exception:
                    if hasattr(file_or_path, "seek"):
                        file_or_path.seek(0)
                    df = pd.read_excel(file_or_path)

    if df is None or df.empty:
        return pd.DataFrame()

    # Normalize column names for flexible matching (strip whitespace)
    col_mapping = {col: str(col).strip() for col in df.columns}
    df = df.rename(columns=col_mapping)
    columns_lower = {str(col).lower().replace(" ", "").replace("_", ""): col for col in df.columns}

    # 1. Review text column
    text_candidates = [
        "reviewtext", "review", "리뷰내용", "리뷰본문", "리뷰", "내용", "본문", "상품평", "후기", "content", "text"
    ]
    matched_text_col = None
    for cand in text_candidates:
        if cand in columns_lower:
            matched_text_col = columns_lower[cand]
            break

    if matched_text_col is None:
        # Pick the column with the highest average string length
        best_col, max_len = df.columns[0], 0
        for col in df.columns:
            try:
                avg_len = df[col].astype(str).str.len().mean()
                if avg_len > max_len:
                    max_len = avg_len
                    best_col = col
            except:
                pass
        matched_text_col = best_col

    df["review_text"] = df[matched_text_col].fillna("").astype(str)

    # 2. Rating column
    rating_candidates = ["rating", "평점", "별점", "점수", "score", "stars"]
    matched_rating_col = None
    for cand in rating_candidates:
        if cand in columns_lower:
            matched_rating_col = columns_lower[cand]
            break

    if matched_rating_col is not None:
        def parse_rating(val):
            if pd.isna(val):
                return 5
            val_str = str(val).strip()
            # Extract first digit 1-5
            m = re.search(r"[1-5]", val_str)
            if m:
                return int(m.group(0))
            try:
                return int(float(val))
            except:
                return 5
        df["rating"] = df[matched_rating_col].apply(parse_rating)
    else:
        df["rating"] = 5

    # 3. Photo / Image indicator
    photo_candidates = [
        "photo", "photourls", "imagecount", "포토", "포토유무", "포토여부",
        "사진", "사진유무", "사진여부", "이미지", "포토리뷰", "포토동영상", "hasphoto"
    ]
    matched_photo_col = None
    for cand in photo_candidates:
        if cand in columns_lower:
            matched_photo_col = columns_lower[cand]
            break

    if matched_photo_col is not None:
        def parse_photo_info(val):
            if pd.isna(val):
                return [], 0
            val_str = str(val).strip()
            if val_str.upper() in ["Y", "O", "포토", "TRUE", "1", "YES"]:
                return ["https://via.placeholder.com/300?text=Customer+Photo"], 1
            if val_str.startswith("http"):
                urls = [u.strip() for u in val_str.split(",") if u.strip().startswith("http")]
                return urls, len(urls)
            if val_str.startswith("[") and val_str.endswith("]"):
                try:
                    parsed = json.loads(val_str.replace("'", '"'))
                    if isinstance(parsed, list):
                        return parsed, len(parsed)
                except:
                    pass
            try:
                num = int(float(val_str))
                if num > 0:
                    return ["https://via.placeholder.com/300?text=Customer+Photo"], num
            except:
                pass
            return [], 0

        photo_results = df[matched_photo_col].apply(parse_photo_info)
        df["photo_urls"] = [r[0] for r in photo_results]
        df["image_count"] = [r[1] for r in photo_results]
    else:
        if "photo_urls" not in df.columns:
            df["photo_urls"] = [[] for _ in range(len(df))]
        if "image_count" not in df.columns:
            df["image_count"] = 0

    # 4. Option name
    option_candidates = ["optionname", "option", "옵션", "선택옵션", "구매옵션", "상품옵션"]
    matched_opt_col = None
    for cand in option_candidates:
        if cand in columns_lower:
            matched_opt_col = columns_lower[cand]
            break
    if matched_opt_col is not None:
        df["option_name"] = df[matched_opt_col].fillna("기본 옵션").astype(str)
    elif "option_name" not in df.columns:
        df["option_name"] = "기본 상품 옵션"

    # 5. User ID
    user_candidates = ["userid", "작성자", "작성자id", "구매자", "아이디", "author", "writer"]
    matched_user_col = None
    for cand in user_candidates:
        if cand in columns_lower:
            matched_user_col = columns_lower[cand]
            break
    if matched_user_col is not None:
        df["user_id"] = df[matched_user_col].fillna("고객***").astype(str)
    elif "user_id" not in df.columns:
        df["user_id"] = [f"user_{i+1:03d}***" for i in range(len(df))]

    # 6. Created date
    date_candidates = ["createddate", "date", "작성일", "등록일", "날짜", "createdat"]
    matched_date_col = None
    for cand in date_candidates:
        if cand in columns_lower:
            matched_date_col = columns_lower[cand]
            break
    if matched_date_col is not None:
        df["created_date"] = df[matched_date_col].fillna("2026.07.01").astype(str)
    elif "created_date" not in df.columns:
        df["created_date"] = "2026.07.01"

    # 7. Review ID
    if "review_id" not in df.columns:
        df["review_id"] = [f"rev_{i+1:04d}" for i in range(len(df))]

    # Calculate text length
    df["text_length"] = df["review_text"].apply(lambda x: len(str(x)))
    return df


def load_reviews_from_csv(file_or_path) -> pd.DataFrame:
    """Backward-compatible alias for load_reviews_from_file."""
    return load_reviews_from_file(file_or_path)



def parse_reviews_from_text(raw_text: str) -> pd.DataFrame:
    """
    Parses pasted text containing customer reviews into a standardized DataFrame.
    Supports reviews separated by empty lines, numbered entries, or bullet points.
    """
    if not raw_text or not raw_text.strip():
        return pd.DataFrame()

    # Split by double newlines or numbered review patterns
    blocks = [b.strip() for b in re.split(r"\n\s*\n+", raw_text) if len(b.strip()) > 5]
    if len(blocks) <= 1:
        # Try splitting by numbered patterns like '1. ', '[리뷰 1]', '리뷰 1:'
        pattern_splits = re.split(r"(?:^|\n)(?:\[?리뷰\s*\d+\]?|\d+[.)])\s*", raw_text)
        candidate_blocks = [b.strip() for b in pattern_splits if len(b.strip()) > 10]
        if len(candidate_blocks) > 1:
            blocks = candidate_blocks
        else:
            # Fallback to single line splits
            blocks = [line.strip() for line in raw_text.split("\n") if len(line.strip()) > 15]

    records = []
    for idx, block in enumerate(blocks):
        rating = extract_rating_from_text(block[:30])
        clean_text = re.sub(r"^(?:\[리뷰\s*\d+\]|리뷰\s*\d+[:.]?|\d+[.)]|\*|-)\s*", "", block).strip()
        if not clean_text:
            continue

        records.append({
            "review_id": f"paste_rev_{idx+1:03d}",
            "user_id": f"user_{idx+1:03d}***",
            "rating": rating,
            "created_date": "2026.07.01",
            "option_name": "스마트스토어 상품 옵션",
            "review_text": clean_text,
            "photo_urls": [],
            "image_count": 0,
            "text_length": len(clean_text)
        })

    return pd.DataFrame(records)


def filter_high_quality_reviews(
    df: pd.DataFrame,
    min_length: int = 100,
    require_photo: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Deterministic filtering logic:
    Filters reviews based on text length (>= min_length) and photo presence (image_count >= 1).
    
    Returns:
        (filtered_df, stats_dict)
    """
    if df.empty:
        return df, {
            "total_count": 0,
            "filtered_count": 0,
            "pass_rate_pct": 0.0,
            "avg_rating": 0.0
        }

    condition = df["text_length"] >= min_length
    if require_photo:
        condition = condition & (df["image_count"] >= 1)

    filtered_df = df[condition].copy()
    
    total_count = len(df)
    filtered_count = len(filtered_df)
    pass_rate_pct = round((filtered_count / total_count * 100), 1) if total_count > 0 else 0.0
    avg_rating = round(float(filtered_df["rating"].mean()), 2) if filtered_count > 0 else 0.0

    stats = {
        "total_count": total_count,
        "filtered_count": filtered_count,
        "pass_rate_pct": pass_rate_pct,
        "avg_rating": avg_rating,
        "min_length_threshold": min_length,
        "require_photo": require_photo
    }

    return filtered_df, stats


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Naver Smartstore Review Scraper & Filter")
    parser.add_argument("--url", type=str, help="Product URL to scrape")
    parser.add_argument("--csv", type=str, help="Existing CSV file to filter")
    parser.add_argument("--min-len", type=int, default=100, help="Minimum review length (default: 100)")
    parser.add_argument("--no-photo-filter", action="store_true", help="Do not require photos")
    parser.add_argument("--max-pages", type=int, default=2, help="Max pages to scrape")
    parser.add_argument("--output", type=str, default="filtered_reviews.csv", help="Output file path")
    args = parser.parse_args()

    if args.url:
        print(f"Scraping {args.url}...")
        df = scrape_smartstore_reviews(args.url, max_pages=args.max_pages, headless=False)
    elif args.csv:
        print(f"Loading {args.csv}...")
        df = load_reviews_from_csv(args.csv)
    else:
        from sample_data import get_sample_dataframe
        print("No URL or CSV specified. Using sample reviews dataset...")
        df = get_sample_dataframe()

    filtered_df, stats = filter_high_quality_reviews(
        df,
        min_length=args.min_len,
        require_photo=not args.no_photo_filter
    )
    
    print("\n" + "="*50)
    print("수집 및 필터링 결과 통계:")
    print(f"- 전체 수집 리뷰: {stats['total_count']}건")
    print(f"- 고품질 필터 통과 리뷰: {stats['filtered_count']}건")
    print(f"- 필터 통과율: {stats['pass_rate_pct']}%")
    print(f"- 통과 리뷰 평균 평점: ★ {stats['avg_rating']}")
    print("="*50)

    filtered_df.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"필터링된 리뷰를 '{args.output}'에 저장했습니다.")
