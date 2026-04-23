import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="Gemini TV 기구 분석 툴", layout="wide")

st.title("📺 Gemini TV 기구 사양 분석 툴 (Google Search 기반)")
st.caption("제미나이의 실시간 구글 검색 기능을 사용하여 경쟁사 기구 스펙을 비교합니다.")

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    st.info("AI Studio에서 발급받은 키를 입력하세요.")

# 2. 사용자 입력
col1, col2, col3 = st.columns(3)
with col1:
    model_1 = st.text_input("비교군 1", placeholder="예: LG OLED65G4")
with col2:
    model_2 = st.text_input("비교군 2", placeholder="예: Samsung QN65QN90D")
with col3:
    model_3 = st.text_input("비교군 3", placeholder="예: Sony XR-65A95L")

# 3. 분석 실행
if st.button("실시간 데이터 분석 시작"):
    if not gemini_api_key:
        st.error("Gemini API Key를 입력해주세요.")
    elif not (model_1 or model_2):
        st.warning("최소 2개 이상의 모델명을 입력해주세요.")
    else:
        try:
            # Gemini 설정
            genai.configure(api_key=gemini_api_key)
            
            # 구글 검색 도구(Grounding) 활성화 설정
            # 모델은 가장 빠르고 효율적인 gemini-1.5-flash를 사용합니다.
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                tools=[{"google_search_retrieval": {}}] 
            )

            with st.spinner("구글 검색을 통해 기구 사양을 수집하고 있습니다..."):
                prompt = f"""
                TV 기구 설계 전문가로서, 다음 모델들의 최신 기구 사양을 구글 검색으로 찾아 비교표를 작성하라:
                모델명: {model_1}, {model_2}, {model_3}

                [필수 포함 항목]
                1. 두께 (최박부/최후부)
                2. 베젤 너비 (L/R/Top/Bottom 또는 전체적인 특징)
                3. 스탠드 구조 및 재질
                4. 후면 커버 공법 및 재질 (Plastic/Metal/Texture 등)
                5. VESA 규격 및 무게(스탠드 제외)
                6. 기구 설계 관점에서의 특징 요약 (예: 보더리스 디자인, 방열 구조 등)

                결과는 깔끔한 마크다운 표 형식으로 출력하라.
                """

                response = model.generate_content(prompt)
                
                st.markdown("### 📊 실시간 기구 사양 비교 결과")
                st.markdown(response.text)
                
                # 출처(Grounding Metadata) 표시 (선택 사항)
                if response.candidates[0].grounding_metadata.search_entry_point:
                    st.caption("정보 출처: Google Search 기반 데이터")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
