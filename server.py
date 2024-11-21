from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from recommend import get_recommended_items
from warning import get_item_warning  # warring.py에서 함수 가져오기
from peaktime import get_current_people_count  # peaktime.py에서 함수 가져오기

# FastAPI 인스턴스 생성
app = FastAPI()

# 요청 바디 모델 정의
class UserCodeRequest(BaseModel):
    userCode: str

# 로그 설정
logging.basicConfig(level=logging.INFO)

@app.post("/OringAI/recommend_item/")
async def recommend_item(request: UserCodeRequest):
    user_code = request.userCode
    recommended_items = get_recommended_items(user_code)
    return {"item_name": recommended_items}

@app.post("/OringAI/item_warning/")
async def item_warning(request: UserCodeRequest):
    user_code = request.userCode
    item_name = get_item_warning(user_code)  # warring.py의 함수 호출
    return {"item_name": item_name}

@app.get("/OringAI/peak_time/")
async def peek_time():
    # 현재 인원 수를 가져오기
    current_people_count = await get_current_people_count()

    # 10명 이상이면 True, 아니면 False 반환
    warning = current_people_count >= 3

    return {"warning": warning}

# 프로그램 시작
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    