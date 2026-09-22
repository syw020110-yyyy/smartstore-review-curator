"""
LLM Summarization & Insight Pipeline Module
Extracts recurring satisfaction themes, copywriting headlines, and representative quotes
from curated customer reviews using the Google Gemini API (Structured Output).
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
import pandas as pd
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Structured Output Schema
# ---------------------------------------------------------------------------
class ThemeInsight(BaseModel):
    theme_name: str = Field(
        description="반복 만족 테마 명칭 (예: '비린내 없는 깔끔한 감칠맛', '탱글탱글한 탄력 식감', '간장 활용도 & 가성비')"
    )
    description: str = Field(
        description="고객들이 해당 요소에 만족한 이유 및 반응에 대한 심층 요약 분석"
    )
    frequency_ratio: str = Field(
        description="해당 테마의 언급 빈도 또는 만족 비중 추정치 (예: '45%', '30%')"
    )
    headline_copy: str = Field(
        description="상세페이지 상단 배너나 소구점 헤드카피로 즉시 사용할 수 있는 매력적인 카피라이팅 문구"
    )
    representative_quotes: List[str] = Field(
        description="해당 테마를 뒷받침하는 실제 고객 원본 리뷰 인용 문장 2~3개 (고객의 생생한 표현 그대로)"
    )


class ReviewAnalysisResult(BaseModel):
    themes: List[ThemeInsight] = Field(
        description="추출된 상위 3~5개 반복 만족 테마 목록"
    )
    overall_summary: str = Field(
        description="전체 리뷰의 핵심 종합 총평 및 고객 관점의 핵심 구매 결정 요인"
    )
    actionable_tips: List[str] = Field(
        description="상세페이지 기획자 및 마케터를 위한 구체적인 상세페이지 개선/배치 제안 3가지"
    )


# ---------------------------------------------------------------------------
# Gemini API Analysis Pipeline
# ---------------------------------------------------------------------------
def analyze_reviews_with_gemini(
    reviews_data: Union[pd.DataFrame, List[str], List[Dict[str, Any]]],
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash"
) -> ReviewAnalysisResult:
    """
    Analyzes customer reviews using the Google Gemini API with Structured Output.
    
    Args:
        reviews_data: pd.DataFrame with 'review_text' or list of review texts/dicts
        api_key: Google Gemini API key (reads from GEMINI_API_KEY env if not provided)
        model_name: Gemini model name (default: gemini-3.6-flash)
        
    Returns:
        ReviewAnalysisResult pydantic model instance
    """
    from google import genai
    from google.genai import types

    # Resolve API key
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key or resolved_api_key.strip() == "":
        raise ValueError(
            "Gemini API 키가 제공되지 않았습니다. 사이드바에 API 키를 입력하거나 GEMINI_API_KEY 환경변수를 설정해주세요."
        )

    # Extract review text lines
    review_texts: List[str] = []
    if isinstance(reviews_data, pd.DataFrame):
        col = "review_text" if "review_text" in reviews_data.columns else reviews_data.columns[0]
        review_texts = reviews_data[col].dropna().astype(str).tolist()
    elif isinstance(reviews_data, list):
        for item in reviews_data:
            if isinstance(item, dict):
                review_texts.append(str(item.get("review_text", item.get("review", ""))))
            else:
                review_texts.append(str(item))

    if not review_texts:
        raise ValueError("분석할 리뷰 데이터가 비어 있습니다.")

    # Format reviews for prompt (select top 30 most informative reviews to guarantee ultra-fast response)
    sorted_reviews = sorted(review_texts, key=lambda x: len(str(x)), reverse=True)[:30]
    formatted_reviews = "\n\n".join(
        [f"[리뷰 {i+1}]: {text.strip()}" for i, text in enumerate(sorted_reviews)]
    )

    prompt = f"""
당신은 대한민국 최고의 이커머스 상세페이지 기획자이자 전환율 최적화(CRO) 마케팅 전문가입니다.
아래는 네이버 스마트스토어에서 실제 구매 고객들이 작성한 100자 이상의 고관여/포토 리뷰 데이터입니다.

고객들이 반복적으로 칭찬하고 만족한 핵심 소구점(Point of Parity & Difference)을 찾아내고,
이를 상세페이지 개선에 즉시 적용할 수 있도록 분석해주세요.

### 분석 지침:
1. **반복 만족 테마 3~5개 도출**:
   - 고객들이 공통적으로 환호하는 3~5개의 핵심 테마를 분류하세요 (예: 식감/품질, 간/양념 밸런스, 손질 편의성, 배송/보냉 안심, 가족/아이 입맛 등).
2. **비중 추정 (frequency_ratio)**:
   - 해당 테마가 전체 만족 리뷰 중 대략 어느 정도의 비중을 차지하는지 퍼센트(예: '45%')로 추정하세요.
3. **상세페이지 헤드카피 (headline_copy)**:
   - 상세페이지 상단 롤링 배너나 핵심 소구점 블록에 바로 실을 수 있는 매력적이고 직관적인 마케팅 카피를 작성하세요.
   - 진부한 문구("최고의 맛") 대신, 고객의 언어를 반영한 생생한 문구("비린내에 예민한 중학생 아들도 밥 세 공기 비운 비결")를 사용하세요.
4. **대표 원본 인용구 (representative_quotes)**:
   - 각 테마마다 고객이 실제로 작성한 원본 문장을 2~3개 그대로 인용하여 신뢰도를 확보하세요.
5. **종합 총평 (overall_summary)**:
   - 이 제품이 고객에게 사랑받는 결정적 이유와 브랜드가 유지해야 할 핵심 가치를 3~4문장으로 요약하세요.
6. **실행 제안 (actionable_tips)**:
   - 상세페이지 디자이너와 기획자가 즉시 실행할 수 있는 실천 팁 3가지를 제안하세요 (예: '남은 맛간장 활용 레시피' 섹션 추가, '보냉 안심 패키지' 언박싱 GIF 배치 등).

---
### 분석 대상 고객 리뷰 목록:
{formatted_reviews}
"""

    logger.info(f"Gemini API 초고속 호출 중 (모델: {model_name}, 선별 분석 리뷰: {len(sorted_reviews)}건)...")

    client = genai.Client(api_key=resolved_api_key)
    
    import time

    def call_gemini(target_model: str, max_retries: int = 2):
        last_error = None
        for attempt in range(max_retries):
            # Attempt with minimal/zero thinking budget for instant output
            try:
                try:
                    tc = types.ThinkingConfig(thinking_budget=0, thinking_level="minimal")
                except:
                    tc = types.ThinkingConfig(thinking_budget=0)

                res = client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ReviewAnalysisResult,
                        temperature=0.2,
                        thinking_config=tc,
                    )
                )
                return res
            except Exception as call_err:
                err_str = str(call_err)
                # If model rejects thinking_config, retry without thinking_config immediately
                if "thinking" in err_str.lower() or "not supported" in err_str.lower():
                    try:
                        return client.models.generate_content(
                            model=target_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=ReviewAnalysisResult,
                                temperature=0.2,
                            )
                        )
                    except Exception as err2:
                        call_err = err2
                        err_str = str(err2)

                last_error = call_err
                # If temporary spike (503 / 429), wait 1s and retry once
                if ("503" in err_str or "429" in err_str or "unavailable" in err_str.lower() or "high demand" in err_str.lower()) and attempt < max_retries - 1:
                    logger.warning(f"[{target_model}] 일시적 트래픽 집중(503/429) 감지. 1초 후 재시도 ({attempt+1}/{max_retries})...")
                    time.sleep(1)
                    continue
                break
        raise last_error

    response = None
    try:
        response = call_gemini(model_name)
    except Exception as e:
        err_msg = str(e)
        # Check if error is 503 (high demand), 429 (rate limit), or 404 (not found)
        is_recoverable = any(code in err_msg for code in ["503", "429", "404"]) or any(
            term in err_msg.lower() for term in ["unavailable", "high demand", "not found", "no longer available", "resource_exhausted"]
        )
        if is_recoverable:
            # Query live models from user's account if possible
            live_candidates = []
            try:
                for m in client.models.list():
                    m_id = m.name.replace("models/", "")
                    actions = getattr(m, "supported_actions", []) or []
                    if "generateContent" in actions:
                        live_candidates.append(m_id)
            except Exception as list_err:
                logger.debug(f"모델 목록 조회 실패: {list_err}")

            if not live_candidates:
                live_candidates = [
                    "gemini-3.5-flash",
                    "gemini-3.5-flash-lite",
                    "gemini-3.7-flash",
                    "gemini-3.8-flash",
                    "gemini-3.6-flash",
                    "gemini-2.5-flash",
                ]

            fallback_candidates = [m for m in live_candidates if m != model_name]
            fallback_success = False
            last_err = e
            for fb_model in fallback_candidates:
                logger.warning(f"모델 '{model_name}' 호출 지연/불가 ({err_msg[:120]}). 활성 대체 모델 '{fb_model}'로 자동 전환 시도...")
                try:
                    response = call_gemini(fb_model, max_retries=2)
                    fallback_success = True
                    logger.info(f"대체 모델 '{fb_model}'로 분석 완료!")
                    break
                except Exception as fb_err:
                    last_err = fb_err
            if not fallback_success:
                raise last_err
        else:
            raise e

    if not response.text:
        raise RuntimeError("Gemini API로부터 빈 응답을 받았습니다.")

    # Parse and validate structured output
    result_data = json.loads(response.text)
    validated_result = ReviewAnalysisResult.model_validate(result_data)
    return validated_result


# ---------------------------------------------------------------------------
# Offline / Demo Mock Result Generator
# ---------------------------------------------------------------------------
def get_mock_analysis_result(reviews_data: Optional[Any] = None) -> ReviewAnalysisResult:
    """
    Returns a rich, authentic mock analysis result for demonstration and offline testing.
    """
    return ReviewAnalysisResult(
        themes=[
            ThemeInsight(
                theme_name="비린내 제로 & 감칠맛 도는 저염 양념",
                description="해산물 특유의 비린 향이 전혀 없고, 지나치게 짜지 않으면서 달콤 짭조름한 감칠맛으로 입맛 까다로운 가족 구성원까지 모두 만족시킴.",
                frequency_ratio="48%",
                headline_copy="\"비린 거 질색하는 아들도 밥 세 공기 뚝딱!\" 텁텁함 없는 순수 저염 감칠맛",
                representative_quotes=[
                    "새우장 좋아하는 까다로운 중학생 아들이 다른 곳 새우장은 비리다고 절대 안 먹는데, 여기꺼 먹더니 '엄마 여기 새우는 비린 맛 하나도 없고 진짜 달아' 하면서 밥 세 그릇을 비우네요.",
                    "비린내에 정말 민감해서 굴이나 게장도 잘 못 먹는데 이건 신기할 정도로 비린 향이 하나도 안 나고 고소하고 감칠맛만 남아요.",
                    "간장 양념이 너무 짜지도 않고 달달하면서 감칠맛이 돌아서 국물까지 밥에 비벼 먹었습니다."
                ]
            ),
            ThemeInsight(
                theme_name="탱글탱글 씹는 맛이 살아있는 탄력 식감",
                description="살이 물렁거리거나 퍼지지 않고 한입 베어 물었을 때 톡 터지는 쫀득한 탄력감과 신선도가 고객들의 최다 찬사를 받음.",
                frequency_ratio="36%",
                headline_copy="한 입 베어 무는 순간 톡 터지는 쫀득함! 차원이 다른 통통한 새우 살의 탄력",
                representative_quotes=[
                    "새우살이 진짜 통통하고 씹는 순간 톡 터지는 쫄깃쫄깃한 식감이 일품이에요!",
                    "전국 유명 맛집 다 시켜먹어봤는데, 일단 입에 넣었을 때 살이 물렁거리지 않고 탱탱 쫀득하게 씹히는 탄력감 자체가 완전히 다릅니다!!"
                ]
            ),
            ThemeInsight(
                theme_name="완벽 손질의 편리함 & 남은 맛간장 200% 활용성",
                description="껍질이 모두 손질되어 번거로움 없이 즉시 섭취 가능하며, 남은 간장을 계란밥, 장조림 등 만능 맛간장으로 재활용하는 가성비 만족도 높음.",
                frequency_ratio="28%",
                headline_copy="손에 묻힐 필요 없이 젓가락으로 쏙! 남은 간장까지 계란밥으로 즐기는 알짜배기 가성비",
                representative_quotes=[
                    "새우 껍질이 다 까져있어서 손에 묻힐 필요 없이 젓가락으로 쏙쏙 집어먹기만 하면 되니까 먹기가 너무 편하고 위생적입니다.",
                    "남은 간장이 진짜 만능 맛간장이에요. 버리기 너무 아까워서 사장님 추천대로 간장계란밥 해먹고 메추리알 장조림까지 만들었습니다."
                ]
            ),
            ThemeInsight(
                theme_name="여름철에도 안심인 철통 신선 보냉 포장",
                description="드라이아이스와 보냉팩이 꽝꽝 언 채로 도착하여 파손이나 누수 없이 신선도를 그대로 유지해 선물용으로도 안심하고 재구매함.",
                frequency_ratio="22%",
                headline_copy="한여름 택배도 갓 잡은 신선함 그대로! 간장 한 방울 새지 않는 안심 3중 패키징",
                representative_quotes=[
                    "여름철이라 해산물 택배 주문하는 게 조금 걱정스러웠는데, 보냉팩이랑 드라이아이스가 아직 꽝꽝 얼어있는 상태로 도착해서 감동했습니다.",
                    "아이스박스에 보냉팩 빵빵하게 채워져서 신선도 완벽하게 배송되었습니다. 포장도 선물하기 좋게 세련되었어요."
                ]
            )
        ],
        overall_summary="본 상품은 '비린내 없는 깔끔한 저염 감칠맛'과 '살아있는 탱글탱글한 탄력 식감'이 강력한 재구매를 이끄는 핵심 요인입니다. 특히 가족 구성원(어린이/남편)의 입맛을 사로잡은 리뷰가 많으며, 껍질 손질 편의성과 남은 맛간장 활용도가 추가적인 가성비 만족도를 크게 높여주고 있습니다.",
        actionable_tips=[
            "1. 상세페이지 최상단에 '비린내 걱정 ZERO' 및 '어린이/까다로운 입맛 검증' 고객 VOC 헤드카피를 메인 비주얼과 함께 배치하세요.",
            "2. '남은 특제 맛간장 200% 활용 꿀팁(간장계란밥, 장조림)' 섹션을 상세페이지 중하단에 레시피 카드 형태로 신설하여 가성비 체감을 극대화하세요.",
            "3. 꽝꽝 얼어 도착하는 3중 안심 보냉 포장 언박싱 실물 사진/GIF를 배치하여 여름철 신선도 불안 심리를 사전에 해소하세요."
        ]
    )


def get_supported_models(api_key: Optional[str] = None) -> List[str]:
    """
    Returns the list of valid models supporting generateContent for the given API key.
    If the API call fails or key is empty, returns recommended active Gemini 3.x models.
    """
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if resolved_api_key:
        try:
            from google import genai
            client = genai.Client(api_key=resolved_api_key)
            models = []
            for m in client.models.list():
                m_id = m.name.replace("models/", "")
                actions = getattr(m, "supported_actions", []) or []
                if "generateContent" in actions:
                    models.append(m_id)
            if models:
                # Prioritize flash models then others
                flash = [m for m in models if "flash" in m and "lite" not in m]
                flash_lite = [m for m in models if "flash-lite" in m or "lite" in m]
                pro = [m for m in models if "pro" in m]
                other = [m for m in models if m not in flash and m not in flash_lite and m not in pro]
                return flash + flash_lite + pro + other
        except Exception as e:
            logger.warning(f"Could not list models dynamically: {e}")

    # Fallback to current Gemini 3.x generation
    return [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.8-flash",
    ]


if __name__ == "__main__":
    import sys
    from sample_data import get_sample_dataframe

    print("Testing analyzer with mock data...")
    mock_res = get_mock_analysis_result()
    print(f"Themes found: {len(mock_res.themes)}")
    for t in mock_res.themes:
        print(f"\n[테마] {t.theme_name} ({t.frequency_ratio})")
        print(f"  카피: {t.headline_copy}")
        print(f"  인용: {t.representative_quotes[0][:50]}...")
    print("\nSummary:", mock_res.overall_summary[:100], "...")
    print("Actionable tips:", mock_res.actionable_tips)
