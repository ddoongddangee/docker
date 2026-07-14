import streamlit as st
import requests
import json
import os

# ==========================================
# 1. 환경 설정 및 상수 정의
# ==========================================
# FastAPI 백엔드 주소 (Docker Compose 사용 시 backend 서비스명으로 통신)
# EC2 등 다른 환경 배포 시 쉽게 수정할 수 있도록 환경 변수를 우선적으로 읽고, 기본값을 할당합니다.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000/recommend")

# 플레이 스타일 목록
STYLES = [
    "Guard Player",
    "Top Pressure",
    "Wrestler",
    "Berimbolo",
    "Leg Lock",
    "Scrambler",
    "Submission Hunter",
    "All Rounder"
]

# ==========================================
# 2. 페이지 설정 및 UI 구성
# ==========================================
st.set_page_config(
    page_title="BJJ Training Recommender",
    page_icon="🥋",
    layout="centered"
)

st.title("🥋 주짓수 플레이 스타일 맞춤 트레이닝 추천")
st.markdown("당신의 주짓수(BJJ) 플레이 스타일을 알려주세요. 최적의 웨이트 트레이닝, 카디오, 드릴을 추천해 드립니다.")

# 사용자 입력 폼
with st.form("recommendation_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        selected_style = st.selectbox("플레이 스타일 (Play Style)", STYLES)
        experience = st.selectbox("운동 경력 (Experience)", ["White Belt", "Blue Belt", "Purple Belt", "Brown Belt", "Black Belt"])
        
    with col2:
        goal = st.selectbox("운동 목적 (Goal)", ["근력 강화", "지구력 향상", "유연성/가동성", "체지방 감량", "대회 준비"])
        days = st.slider("주당 운동 가능 횟수 (Days per week)", min_value=1, max_value=7, value=3)
        
    submit_button = st.form_submit_button("추천 받기 (Get Recommendation)")

# ==========================================
# 3. 데이터 처리 및 결과 출력
# ==========================================
if submit_button:
    # FastAPI로 보낼 데이터 준비
    payload = {
        "style": selected_style,
        "experience": experience,
        "goal": goal,
        "days": days
    }
    
    try:
        with st.spinner("최적의 트레이닝 프로그램을 계산 중입니다..."):
            # FastAPI 백엔드로 POST 요청 (추천 계산은 모두 백엔드에서 수행)
            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()
            
            # JSON 응답 파싱
            result = response.json()
            
            # 결과 출력
            st.markdown("---")
            st.subheader(f"💡 {result['style']} 스타일을 위한 추천 트레이닝")
            
            st.info(f"**추천 이유:** {result['reason']}")
            
            col_weight, col_cardio, col_drill = st.columns(3)
            
            with col_weight:
                st.success("🏋️‍♂️ **웨이트 트레이닝**")
                for w in result["weight_training"]:
                    st.markdown(f"- {w}")
                    
            with col_cardio:
                st.warning("🏃‍♂️ **카디오 (Cardio)**")
                for c in result["cardio"]:
                    st.markdown(f"- {c}")
                    
            with col_drill:
                st.error("🥋 **BJJ 드릴 (Drill)**")
                for d in result["drill"]:
                    st.markdown(f"- {d}")
                    
    except requests.exceptions.ConnectionError:
        st.error(f"백엔드 서버({BACKEND_URL})에 연결할 수 없습니다. 서버가 켜져 있는지 확인해주세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
