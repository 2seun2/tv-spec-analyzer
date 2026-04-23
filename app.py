import streamlit as st
import google.generativeai as genai

# 1. 페이지 및 API 설정
st.set_page_config(page_title="TV 신모델 기구 분석 툴", layout="wide")
st.title("📺 TV 제조사별 신모델 기구 사양 분석")

with st.sidebar:
    st.header("설정")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    if not gemini_api_key:
        st.warning("API Key를 입력해야 작동합니다.")

# 2. 제조사 및 인치 선택
st.subheader("1. 비교하고 싶은 제품군 설정")
col_make, col_inch = st.columns(2)

with col_make:
    manufacturers = st.multiselect("제조사 선택", ["Samsung", "LG", "Sony", "TCL", "Hisense"], default=["Samsung", "LG"])
with col_inch:
    inch_size = st.selectbox("화면 크기(Inch)", ["55", "65", "75", "83", "85", "98"], index=1)

# 3. 모델 리스트 확보 (Step 1)
if st.button("해당 조건의 최신 모델 라인업 조회"):
    if not gemini_api_key:
        st.error("API Key를 먼저 입력해주세요.")
    else:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",
                tools=[{"google_search_retrieval": {}}]
            )
            
            with st.spinner(f"{', '.join(manufacturers)}의 {inch_size}인치 최신 모델을 검색 중입니다..."):
                list_prompt = f"2024년~2025년 최신작 기준, {', '.join(manufacturers)} 브랜드의 {inch_size}인치 TV 모델명(Full Model Name) 리스트를 3개 이상 찾아줘."
                list_response = model.generate_content(list_prompt)
                st.info("💡 아래 모델명 중 비교하고 싶은 모델을 복사해서 아래 입력창에 넣어주세요.")
                st.markdown(list_response.text)
        except Exception as e:
            st.error(f"모델 조회 중 오류 발생: {e}")

st.divider()

# 4. 상세 기구 비교 (Step 2)
st.subheader("2. 상세 기구 Spec 비교 분석")
c1, c2, c3 = st.columns(3)
with c1:
    m1 = st.text_input("비교 모델 1", placeholder="조회된 모델명 붙여넣기")
with c2:
    m2 = st.text_input("비교 모델 2", placeholder="조회된 모델명 붙여넣기")
with c3:
    m3 = st.text_input("비교 모델 3 (선택)", placeholder="선택 사항")

if st.button("기구 설계 사양 정밀 비교"):
    if not (m1 and m2):
        st.warning("최소 두 개의 모델명을 입력해주세요.")
    else:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",
                tools=[{"google_search_retrieval": {}}]
            )
            
            with st.spinner("기구 설계 데이터를 분석 중입니다..."):
                spec_prompt = f"""
                TV 기구 설계 전문가로서 아래 모델들의 기구 스펙을 비교 분석하라:
                모델: {m1}, {m2}, {m3}

                [분석 항목]
                1. 본체 두께(최박부 및 가장 두꺼운 곳)
                2. 베젤 폭(On/Off Bezel 구분 가능 시 표기)
                3. 후면 커버 재질 및 표면 처리 공법
                4. 스탠드 유형(Center/Side/Pedestal) 및 재질
                5. VESA 규격 및 무게
                
                결과는 마크다운 표로 작성하고, 마지막에 개발자 관점에서 '박형화'와 '조립성'에 대한 의견을 추가하라.
                """
                spec_response = model.generate_content(spec_prompt)
                st.success("분석 완료!")
                st.markdown(spec_response.text)
        except Exception as e:
            st.error(f"상세 분석 중 오류 발생: {e}")
