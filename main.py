from playwright.sync_api import sync_playwright

PRODUCT_URL = "https://smartstore.naver.com/wcfood172/products/11240293471"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=300
    )

    page = browser.new_page(
        viewport={"width": 1400, "height": 1000}
    )

    print("상품 페이지 접속 중...")

    page.goto(PRODUCT_URL)
    page.wait_for_load_state("networkidle")

    # 리뷰 전체보기 클릭
    page.locator("#REVIEW").get_by_role(
        "button",
        name="리뷰 전체보기"
    ).click()

    page.wait_for_timeout(3000)

    # 리뷰 아이템 찾기
    review_items = page.locator("li[id^='REVIEW_ITEM_']")

    print("=" * 50)
    print("리뷰 아이템 개수 :", review_items.count())
    print("=" * 50)

    # 처음 3개 리뷰만 출력
    for i in range(min(3, review_items.count())):
        print(f"\n===== 리뷰 {i+1} =====")
        print(review_items.nth(i).inner_text())

    input("\n엔터를 누르면 종료됩니다.")

    browser.close()