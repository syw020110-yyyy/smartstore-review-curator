"""
Smartstore Review Curator & Insight Extractor
Streamlit Dashboard Application
"""
import os
import io
import json
import logging
import pandas as pd
import streamlit as st

from scraper import (
    load_reviews_from_file,
    load_reviews_from_csv,
    parse_reviews_from_text,
    filter_high_quality_reviews,
    parse_smartstore_url,
)
from analyzer import (
    analyze_reviews_with_gemini,
    get_mock_analysis_result,
    get_supported_models,
    ReviewAnalysisResult,
)
from sample_data import get_sample_dataframe

# ---------------------------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Smartstore Review Curator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #10b981;
    }
    .review-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s ease-in-out;
    }
    .review-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.4rem;
    }
    .badge-option {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    .badge-len {
        background-color: #f3f4f6;
        color: #374151;
    }
    .badge-photo {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .theme-card {
        background: #ffffff;
        border-left: 5px solid #10b981;
        border-radius: 8px;
        padding: 1.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .headline-box {
        background-color: #f0fdf4;
        border: 1px dashed #86efac;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        font-weight: 700;
        color: #166534;
        font-size: 1.05rem;
        margin: 0.8rem 0;
    }
    .quote-box {
        background-color: #f9fafb;
        border-left: 3px solid #cbd5e1;
        padding: 0.6rem 0.9rem;
        font-size: 0.9rem;
        color: #475569;
        font-style: italic;
        margin-bottom: 0.5rem;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "raw_df" not in st.session_state:
    # Load default sample reviews initially
    st.session_state.raw_df = get_sample_dataframe()
    st.session_state.source_name = "기본 샘플 데이터 (순살 간장새우장)"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

# ---------------------------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shopaholic.png", width=64)
    st.title("Review Curator")
    st.caption("스마트스토어 리뷰 큐레이터 & 인사이트 추출기")
    st.markdown("---")

    # 1. Data Source Selection
    st.subheader("1. 데이터 수집 방식")
    source_type = st.radio(
        "수집 모드 선택",
        [
            "엑셀(.xlsx) / CSV 파일 업로드 (추천)",
            "리뷰 텍스트 직접 붙여넣기",
            "데모 샘플 데이터 체험",
        ],
        index=0,
    )

    if source_type == "엑셀(.xlsx) / CSV 파일 업로드 (추천)":
        st.info("📊 크롬 확장 프로그램이나 스마트스토어에서 추출한 엑셀(.xlsx, .xls) 또는 CSV 파일을 업로드하세요.")
        uploaded_file = st.file_uploader(
            "엑셀 또는 CSV 파일 선택",
            type=["xlsx", "xls", "csv"],
            help="리뷰하운드, 리뷰 수집기, 스마트스토어 등에서 다운로드한 엑셀/CSV 파일을 그대로 올리시면 됩니다."
        )
        if uploaded_file is not None:
            try:
                with st.spinner("파일을 읽고 표준 데이터로 변환 중..."):
                    loaded_df = load_reviews_from_file(uploaded_file)
                if loaded_df.empty:
                    st.warning("파일에서 유효한 리뷰 데이터를 찾을 수 없습니다. 파일 내용과 열 구성을 확인해주세요.")
                else:
                    st.session_state.raw_df = loaded_df
                    st.session_state.source_name = f"업로드 파일 ({uploaded_file.name})"
                    st.session_state.analysis_result = None
                    st.success(f"총 {len(loaded_df):,}개의 리뷰를 성공적으로 불러왔습니다!")
            except Exception as err:
                st.error(f"파일 로딩 에러: {err}")

    elif source_type == "리뷰 텍스트 직접 붙여넣기":
        st.info("📋 웹 브라우저에서 리뷰를 복사(Ctrl+C)하여 아래에 붙여넣으세요.")
        pasted_text = st.text_area(
            "리뷰 텍스트 붙여넣기 (여러 리뷰를 엔터로 구분)",
            placeholder="""예시:
새우장 좋아하는 중학생 아들이 다른 곳 새우장은 비리다고 안 먹는데 여기 건 비린내 하나도 없고 달아서 밥 세 그릇 비우네요!

살이 진짜 통통하고 쫄깃쫄깃합니다. 간장도 안 짜고 감칠맛이 돌아서 계란밥 해먹기 딱 좋습니다. 재구매 100%입니다!""",
            height=180
        )
        if st.button("📥 붙여넣은 리뷰 로드 및 분석", type="primary", use_container_width=True):
            if not pasted_text.strip():
                st.error("붙여넣은 리뷰 텍스트가 없습니다.")
            else:
                p_df = parse_reviews_from_text(pasted_text)
                if p_df.empty:
                    st.warning("유효한 리뷰 텍스트를 인식하지 못했습니다.")
                else:
                    st.session_state.raw_df = p_df
                    st.session_state.source_name = f"직접 붙여넣은 리뷰 ({len(p_df)}건)"
                    st.session_state.analysis_result = None
                    st.success(f"총 {len(p_df)}개의 리뷰를 성공적으로 불러왔습니다! ('포토 첨부 필수' 체크 해제 권장)")

    else:  # 데모 샘플 데이터
        st.info("📦 실제 스마트스토어 새우장 상품의 검증된 샘플 리뷰 15건을 사용합니다.")
        if st.button("🔄 샘플 데이터 다시 로드", use_container_width=True):
            st.session_state.raw_df = get_sample_dataframe()
            st.session_state.source_name = "기본 샘플 데이터 (순살 간장새우장)"
            st.session_state.analysis_result = None
            st.success("샘플 데이터를 성공적으로 불러왔습니다.")

    st.markdown("---")

    # 2. Deterministic Filter Thresholds
    st.subheader("2. 결정적 필터링 기준")
    min_length = st.slider(
        "최소 리뷰 글자 수",
        min_value=30,
        max_value=300,
        value=100,
        step=10,
        help="단답형('좋아요', '빨라요') 리뷰를 배제하고 고관여 리뷰만 필터링합니다.",
    )
    require_photo = st.checkbox(
        "포토 첨부 필수 (image_count >= 1)",
        value=True,
        help="상세페이지에 실을 수 있는 실물 사진이 포함된 리뷰만 선별합니다.",
    )

    st.markdown("---")

    # 3. Gemini API Configuration
    st.subheader("3. Google Gemini 설정")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIzaSy...",
        help="Google AI Studio에서 발급받은 Gemini API 키를 입력하세요.",
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input

    @st.cache_data(ttl=1800, show_spinner=False)
    def _fetch_models(k: str):
        return get_supported_models(k)

    available_models = _fetch_models(st.session_state.gemini_api_key)
    model_choice = st.selectbox(
        "Gemini 모델",
        available_models,
        index=0,
        help="사용 중인 Gemini API 키에서 지원하는 실제 활성 모델 목록입니다.",
    )

    if st.session_state.gemini_api_key:
        st.success("🔑 Gemini API 키 연결됨")
    else:
        st.caption("ℹ️ API 키가 없어도 '데모 분석'으로 즉시 체험 가능합니다.")

# ---------------------------------------------------------------------------
# Filter Processing
# ---------------------------------------------------------------------------
raw_df = st.session_state.raw_df
filtered_df, stats = filter_high_quality_reviews(
    raw_df,
    min_length=min_length,
    require_photo=require_photo
)

# ---------------------------------------------------------------------------
# Main Header & Metrics
# ---------------------------------------------------------------------------
st.markdown('<div class="main-header">Smartstore Review Curator & Insight Extractor</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">데이터 출처: <b>{st.session_state.source_name}</b> | 상세페이지 즉시 활용을 위한 고품질 포토리뷰 큐레이션 및 AI 소구점 분석 도구</div>',
    unsafe_allow_html=True
)

# Top KPI Metric Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">총 수집 리뷰</div>
        <div class="kpi-value" style="color: #3b82f6;">{stats['total_count']:,}건</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">고품질 필터 통과 리뷰</div>
        <div class="kpi-value" style="color: #10b981;">{stats['filtered_count']:,}건</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">필터 통과율</div>
        <div class="kpi-value" style="color: #8b5cf6;">{stats['pass_rate_pct']}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    stars = "★" * int(round(stats['avg_rating'])) if stats['avg_rating'] > 0 else "-"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">통과 리뷰 평균 평점</div>
        <div class="kpi-value" style="color: #f59e0b;">★ {stats['avg_rating']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tab Views
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📸 큐레이션된 고품질 포토리뷰", "💡 상세페이지 기획 인사이트 (Gemini AI)"])

# ---------------------------------------------------------------------------
# Tab 1: Filtered Reviews View
# ---------------------------------------------------------------------------
with tab1:
    if filtered_df.empty:
        st.warning("⚠️ 현재 필터 조건(글자 수, 포토 여부)을 만족하는 리뷰가 없습니다. 사이드바에서 임계값을 조정해주세요.")
    else:
        # Action bar: search, sort, and download buttons
        action_col1, action_col2, action_col3, action_col4 = st.columns([3, 2, 1.5, 1.5])
        with action_col1:
            search_query = st.text_input("🔍 리뷰 내용/옵션 검색", placeholder="키워드 입력 (예: 식감, 아들, 간장)...")
        with action_col2:
            sort_by = st.selectbox("정렬 기준", ["글자수 많은순", "평점 높은순", "최신순"])
        with action_col3:
            # CSV Download
            csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name="curated_smartstore_reviews.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with action_col4:
            # Excel Download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                filtered_df.to_excel(writer, index=False, sheet_name="고품질리뷰")
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="📊 Excel 다운로드",
                data=excel_data,
                file_name="curated_smartstore_reviews.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        # Apply search and sorting
        display_df = filtered_df.copy()
        if search_query:
            display_df = display_df[
                display_df["review_text"].str.contains(search_query, case=False, na=False) |
                display_df["option_name"].str.contains(search_query, case=False, na=False)
            ]

        if sort_by == "글자수 많은순":
            display_df = display_df.sort_values(by="text_length", ascending=False)
        elif sort_by == "평점 높은순":
            display_df = display_df.sort_values(by="rating", ascending=False)
        elif sort_by == "최신순":
            display_df = display_df.sort_values(by="created_date", ascending=False)

        st.caption(f"조건에 맞는 리뷰 총 **{len(display_df)}건**을 표시합니다.")

        # View Mode Toggle: Card View vs Table View
        view_mode = st.radio("보기 형태", ["카드형 갤러리 뷰", "데이터프레임 테이블 뷰"], horizontal=True)

        if view_mode == "카드형 갤러리 뷰":
            for _, row in display_df.iterrows():
                with st.container():
                    st.markdown('<div class="review-card">', unsafe_allow_html=True)
                    
                    # Top meta row
                    col_meta, col_len = st.columns([4, 1])
                    with col_meta:
                        rating_stars = "★" * int(row['rating']) + "☆" * (5 - int(row['rating']))
                        st.markdown(f"<span style='color: #f59e0b; font-weight: 700; font-size: 1.1rem;'>{rating_stars}</span> <b>{row['rating']}점</b> &nbsp;·&nbsp; <span style='color: #6b7280;'>{row['user_id']}</span> &nbsp;·&nbsp; <span style='color: #9ca3af;'>{row['created_date']}</span>", unsafe_allow_html=True)
                    with col_len:
                        st.markdown(f"<div style='text-align: right;'><span class='badge badge-len'>{row['text_length']}자</span></div>", unsafe_allow_html=True)

                    # Option and badges
                    badges_html = ""
                    if row.get("option_name"):
                        badges_html += f"<span class='badge badge-option'>🏷️ {row['option_name']}</span>"
                    if row.get("image_count", 0) > 0:
                        badges_html += f"<span class='badge badge-photo'>📷 포토 {row['image_count']}장</span>"
                    
                    if badges_html:
                        st.markdown(f"<div style='margin-top: 0.3rem; margin-bottom: 0.6rem;'>{badges_html}</div>", unsafe_allow_html=True)

                    # Photos gallery
                    photos = row.get("photo_urls", [])
                    if isinstance(photos, list) and len(photos) > 0:
                        img_cols = st.columns(min(len(photos), 4))
                        for i, p_url in enumerate(photos[:4]):
                            with img_cols[i]:
                                st.image(p_url, use_container_width=True)

                    # Review content
                    st.markdown(f"<div style='font-size: 0.98rem; line-height: 1.6; color: #1f2937; margin-top: 0.5rem;'>{row['review_text']}</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        else:
            # Table View
            st.dataframe(
                display_df[["rating", "created_date", "user_id", "option_name", "text_length", "image_count", "review_text"]],
                use_container_width=True,
                height=500
            )


# ---------------------------------------------------------------------------
# Tab 2: LLM Insight Pipeline (Gemini AI)
# ---------------------------------------------------------------------------
with tab2:
    st.markdown("### 🤖 Google Gemini AI 기반 고객 만족 소구점 & 헤드카피 추출")
    st.write(
        "필터링된 고품질 리뷰들을 클러스터링하여 **반복적으로 칭찬받는 핵심 소구점(Top 3~5 테마)**과 "
        "상세페이지에 바로 복사해 넣을 수 있는 **전환율 최적화 헤드카피**, **실제 고객 원본 인용구**를 자동 생성합니다."
    )

    col_btn1, col_btn2 = st.columns([2, 5])
    with col_btn1:
        run_analysis = st.button("✨ AI 인사이트 분석 실행", type="primary", use_container_width=True)
    with col_btn2:
        if not st.session_state.gemini_api_key:
            run_demo = st.button("🧪 API 키 없이 데모 인사이트 체험하기", use_container_width=False)
            if run_demo:
                st.session_state.analysis_result = get_mock_analysis_result(filtered_df)
                st.success("데모 분석 결과가 로드되었습니다!")

    if run_analysis:
        if filtered_df.empty:
            st.error("분석할 필터 통과 리뷰가 없습니다. 먼저 리뷰를 수집하거나 필터 조건을 완화해주세요.")
        elif not st.session_state.gemini_api_key:
            st.warning("사이드바에 Google Gemini API 키를 입력해주세요. (또는 '데모 인사이트 체험하기' 버튼을 누르시면 즉시 예시 결과를 보실 수 있습니다)")
        else:
            with st.spinner(f"Gemini AI ({model_choice}) 모델이 리뷰를 심층 분석하고 소구점을 추출하는 중입니다..."):
                try:
                    result = analyze_reviews_with_gemini(
                        reviews_data=filtered_df,
                        api_key=st.session_state.gemini_api_key,
                        model_name=model_choice
                    )
                    st.session_state.analysis_result = result
                    st.success("AI 인사이트 분석이 완료되었습니다!")
                except Exception as ex:
                    st.error(f"분석 중 오류가 발생했습니다: {ex}")
                    st.info("💡 팁: API 키가 올바른지 확인하거나, 일시적 네트워크 지연 시 다시 시도해주세요.")

    # Render Analysis Results
    if st.session_state.analysis_result is not None:
        analysis: ReviewAnalysisResult = st.session_state.analysis_result
        
        st.markdown("---")
        
        # Overall Summary Callout
        st.markdown("#### 📌 종합 총평 및 핵심 구매 트리거")
        st.info(analysis.overall_summary)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🏆 빈출 만족 테마 Top 3~5 & 상세페이지 추천 카피")

        # Themes cards
        for idx, theme in enumerate(analysis.themes):
            st.markdown(f"""
            <div class="theme-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem; font-weight: 700; color: #111827;">
                        테마 {idx+1}. {theme.theme_name}
                    </span>
                    <span class="badge" style="background-color: #ecfdf5; color: #059669; font-size: 0.85rem; border: 1px solid #10b981;">
                        만족 비중 약 {theme.frequency_ratio}
                    </span>
                </div>
                <p style="color: #4b5563; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.8rem;">
                    {theme.description}
                </p>
                <div class="headline-box">
                    💡 <b>상세페이지 추천 헤드카피:</b><br>
                    {theme.headline_copy}
                </div>
                <div style="margin-top: 0.8rem;">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #6b7280;">💬 실제 고객 원본 인용구 (Voice of Customer):</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for quote in theme.representative_quotes:
                st.markdown(f'<div class="quote-box">"{quote}"</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Actionable Tips Section
        st.markdown("#### 🎯 상세페이지 기획자를 위한 실행 액션 플랜")
        for tip in analysis.actionable_tips:
            st.markdown(f"- **{tip}**")

        st.markdown("---")

        # Export Analysis Results
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            # Markdown export
            md_lines = [
                f"# 스마트스토어 리뷰 AI 인사이트 보고서\n",
                f"## 1. 종합 총평\n{analysis.overall_summary}\n\n",
                f"## 2. 빈출 만족 테마 및 추천 헤드카피\n"
            ]
            for i, t in enumerate(analysis.themes):
                md_lines.append(f"### 테마 {i+1}: {t.theme_name} (비중: {t.frequency_ratio})")
                md_lines.append(f"- **요약 설명**: {t.description}")
                md_lines.append(f"- **추천 헤드카피**: {t.headline_copy}")
                md_lines.append(f"- **고객 원본 인용구**:")
                for q in t.representative_quotes:
                    md_lines.append(f"  > \"{q}\"")
                md_lines.append("\n")

            md_lines.append("## 3. 상세페이지 기획자 실행 액션 플랜\n")
            for tip in analysis.actionable_tips:
                md_lines.append(f"- {tip}\n")

            md_content = "\n".join(md_lines)
            st.download_button(
                "📄 마크다운 보고서 (.md) 다운로드",
                data=md_content,
                file_name="smartstore_review_insights.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_exp2:
            # JSON export
            json_content = json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2)
            st.download_button(
                "📦 구조화 데이터 (.json) 다운로드",
                data=json_content,
                file_name="smartstore_review_insights.json",
                mime="application/json",
                use_container_width=True
            )
