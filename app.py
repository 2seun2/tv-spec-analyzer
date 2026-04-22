import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

# 1. 페이지 설정
st.set_page_config(page_title="TV 기구 사양 비교 분석 툴", layout="wide")

st.title("📺 TV 기구 개발용 경쟁사 비교 분석 툴")
st.caption("모델명을 입력하면 웹 정보를 검색하여 기구 Spec 비교표를 생성합니다.")

# 사이드바에서 API 키 설정
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("OpenAI API Key", type="password")
    model_choice = st.selectbox("모델 선택", ["gpt-4o", "gpt-4-turbo"])

# 2. 사용자 입력 부분
col1, col2, col3 = st.columns(3)
with col1:
    model_1 = st.text_input("비교군 1 (모델명)", placeholder="예: LG OLED65G3")
with col2:
    model_2 = st.text_input("비교군 2 (모델명)", placeholder="예: Samsung QN65QN90C")
with col3:
    model_3 = st.text_input("비교군 3 (모델명)", placeholder="예: Sony XR-65A95L")

# 3. 분석 로직
def get_web_search_data(model_names):
    """모델별로 웹 검색 결과 요약을 가져옴"""
    search_results = ""
    with DDGS() as ddgs:
        for name in model_names:
            if name:
                results = ddgs.text(f"{name} mechanical specifications dimensions weight bezel vesa", max_results=3)
                search_results += f"\n[Model: {name}]\n"
                for r in results:
                    search_results += f"- {r['body']}\n"
    return search_results

if st.button("데이터 분석 및 비교표 생성"):
    if not api_key:
        st.error("OpenAI API Key를 입력해주세요.")
    elif not (model_1 or model_2):
        st.warning("최소 2개 이상의 모델명을 입력해주세요.")
    else:
        with st.spinner("웹 데이터를 검색하고 기구 사양을 분석 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)
                
                # 웹 데이터 수집
                models = [model_1, model_2, model_3]
                raw_context = get_web_search_data([m for m in models if m])

                # AI 프롬프트 구성
                prompt = f"""
                너는 TV 기구 설계 전문가이다. 아래 제공된 검색 데이터를 바탕으로 모델들의 기구 사양을 비교 분석하라.
                
                [검색 데이터]
                {raw_context}

                [작업 지침]
                1. 검색 데이터를 분석하여 '두께, 베젤, 스탠드, 재질, VESA, 무게' 등 기구 설계 핵심 사양을 추출하라.
                2. 비교군이 3개라면 3개 모두 표에 포함하라. 데이터가 없으면 '확인 불가'로 적어라.
                3. 마크다운 표(Table) 형식으로 출력하라.
                4. 표 하단에 기구 설계자 관점에서 각 모델의 특징(공법 추정, 설계 강점 등)을 3줄 요약하라.

                [출력 양식]
                항목 | {model_1} | {model_2} | {model_3}
                ---|---|---|---
                본체 두께 | | |
                베젤 폭 | | |
                스탠드 구조 | | |
                후면 재질 | | |
                VESA 규격 | | |
                무게 | | |
                """

                response = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "system", "content": "기구 설계 전문가로서 답변하세요."},
                              {"role": "user", "content": prompt}]
                )

                # 결과 출력
                result_text = response.choices[0].message.content
                st.markdown("### 📊 기구 사양 비교 분석 결과")
                st.markdown(result_text)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# 4. 결과 저장 기능 (CSV 다운로드 등) - 필요 시 추가 가능
