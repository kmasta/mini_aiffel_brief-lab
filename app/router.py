# app/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.langgraph_builder import build_pipeline
import traceback

router = APIRouter()
pipeline = build_pipeline()

class RequestModel(BaseModel):
    user_id: str
    keywords: list[str]
    email: str

@router.post("/generate-summary")
async def generate_summary(req: RequestModel):
    state = req.dict()
    try:
        result = pipeline.invoke(state)
        return result
    except Exception as e:
        # 전체 스택 트레이스 터미널 출력
        traceback.print_exc()
        # 문제 생긴 state 덤프
        print("Failed input state:", state)
        raise HTTPException(status_code=500, detail=str(e))