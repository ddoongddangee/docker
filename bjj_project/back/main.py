from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. Pydantic Models (데이터 검증 모델)
# ==========================================

class RecommendRequest(BaseModel):
    """
    프론트엔드로부터 전달받는 사용자 입력 데이터 모델
    """
    style: str = Field(..., description="사용자의 주짓수 플레이 스타일")
    experience: str = Field(..., description="운동 경력")
    goal: str = Field(..., description="운동 목적")
    days: int = Field(..., description="주당 운동 가능 횟수", ge=1, le=7)


class RecommendResponse(BaseModel):
    """
    프론트엔드로 반환하는 추천 결과 데이터 모델
    """
    style: str
    weight_training: List[str]
    cardio: List[str]
    drill: List[str]
    reason: str


# ==========================================
# 2. FastAPI 앱 인스턴스 생성
# ==========================================
app = FastAPI(
    title="BJJ Recommendation API",
    description="브라질리언 주짓수 플레이 스타일별 운동 추천 시스템 백엔드",
    version="1.0.0"
)


# ==========================================
# 3. Rule Engine 데이터베이스 (Dictionary 기반)
# ==========================================
# 최소 8가지 이상의 플레이 스타일별 추천 데이터를 정의합니다.
RECOMMENDATION_DB = {
    "Guard Player": {
        "weight_training": ["Pull up", "Bulgarian Split Squat", "Romanian Deadlift"],
        "cardio": ["Assault Bike Interval", "Rowing Machine"],
        "drill": ["Hip Escape", "Granby Roll", "Inversion Drill"],
        "reason": "가드 플레이어는 상대의 압박을 견디고 끌어당기는 힘(Pulling)과 하체의 유연성/코어가 중요하므로, 당기는 근력 운동과 고관절 움직임을 강화하는 드릴을 추천합니다."
    },
    "Top Pressure": {
        "weight_training": ["Barbell Squat", "Bench Press", "Farmer's Walk"],
        "cardio": ["Heavy Sled Push", "Kettlebell Swings"],
        "drill": ["Knee on Belly Transition", "Toreando Pass Drill", "Sprawl & Crossface"],
        "reason": "탑 프레셔 플레이어는 위에서 누르는 압박감과 베이스가 중요합니다. 전신 스트렝스를 위한 3대 운동과 폭발적인 푸쉬 카디오를 추천합니다."
    },
    "Wrestler": {
        "weight_training": ["Power Clean", "Front Squat", "Overhead Press"],
        "cardio": ["Treadmill Sprints", "Stairmaster"],
        "drill": ["Double Leg Takedown Shadow", "Sprawl", "Pummeling"],
        "reason": "레슬러 스타일은 폭발적인 파워와 지구력이 요구됩니다. 역도성 운동으로 순발력을 기르고, 강도 높은 인터벌 스프린트와 테이크다운 드릴을 추천합니다."
    },
    "Berimbolo": {
        "weight_training": ["Jefferson Curl", "Hanging Leg Raise", "Pistol Squat"],
        "cardio": ["SkiErg", "Jump Rope"],
        "drill": ["Wall Inversion", "Bolo Spin Drill", "Crab Walk"],
        "reason": "베림볼로 플레이어는 척추의 유연성과 코어 컨트롤이 핵심입니다. 극단적인 유연성을 보조하는 운동과 척추 굴곡을 돕는 드릴을 추천합니다."
    },
    "Leg Lock": {
        "weight_training": ["Nordic Hamstring Curl", "Calf Raise", "Hip Thrust"],
        "cardio": ["Stationary Bike (High Resistance)", "VersaClimber"],
        "drill": ["Imanari Roll", "Ashi Garami Entry Drill", "Heel Hook Finish Mechanics"],
        "reason": "레그락 플레이어는 상대 하체를 제압하는 얽힘(Entanglement) 동작이 잦습니다. 하체 후면 사슬을 강화하고 관절 인지력을 높이는 드릴을 추천합니다."
    },
    "Scrambler": {
        "weight_training": ["Kettlebell Turkish Get-Up", "Medicine Ball Throws", "Box Jumps"],
        "cardio": ["Burpees Interval", "Sprint Intervals"],
        "drill": ["Technical Stand-up", "Turtle Reversals", "Wrestling Sit-out"],
        "reason": "스크램블러는 혼전 상황에서 빠르고 변칙적으로 움직여야 합니다. 전신 협응력과 순발력을 기르는 운동 및 카디오를 추천합니다."
    },
    "Submission Hunter": {
        "weight_training": ["Bicep Curls", "Grip Training (Captains of Crush)", "Tricep Extension"],
        "cardio": ["Battle Ropes", "Shadow Grappling"],
        "drill": ["Triangle Choke Setup Drill", "Armbar from Mount", "Guillotine Choke Reps"],
        "reason": "서브미션 헌터는 결정적인 순간에 그립을 쥐고 당기거나 조이는 힘이 중요합니다. 팔과 악력 위주의 고립 운동과 피니쉬 드릴을 추천합니다."
    },
    "All Rounder": {
        "weight_training": ["Deadlift", "Push Press", "Lunge"],
        "cardio": ["5K Run", "Swimming"],
        "drill": ["Guard Pass to Mount", "Escape from Side Control", "Takedown to Pass Combo"],
        "reason": "올라운더는 약점 없는 밸런스가 필요합니다. 전반적인 기초 체력을 올려주는 복합 관절 운동과 기초 드릴을 균형 있게 추천합니다."
    }
}


# ==========================================
# 4. API 엔드포인트 구현
# ==========================================
@app.post("/recommend", response_model=RecommendResponse)
def get_recommendation(request: RecommendRequest):
    """
    사용자의 플레이 스타일 및 정보를 입력받아 맞춤형 추천 데이터를 반환합니다.
    """
    # 1) 사용자가 입력한 스타일이 데이터베이스에 있는지 확인
    style_key = request.style
    if style_key not in RECOMMENDATION_DB:
        # 데이터베이스에 없는 스타일이 들어오면 404 에러 반환
        raise HTTPException(
            status_code=404, 
            detail=f"선택하신 '{style_key}'에 대한 추천 데이터가 없습니다."
        )
    
    # 2) 데이터베이스에서 추천 정보 조회 (Rule Engine 기반)
    data = RECOMMENDATION_DB[style_key]

    # (참고) 입력받은 experience, goal, days를 활용해 추천 로직을 더 세분화할 수도 있으나,
    # 본 과제에서는 '플레이 스타일별로 모두 달라야 한다'는 핵심 규칙을 최우선으로 하여 
    # Dictionary 기반으로 매핑된 결과를 반환합니다.

    # 3) 결과 구성 후 반환
    return RecommendResponse(
        style=style_key,
        weight_training=data["weight_training"],
        cardio=data["cardio"],
        drill=data["drill"],
        reason=data["reason"]
    )
