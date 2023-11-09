from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal

from routers.auth import get_current_user


router = APIRouter(
    prefix='/application',
    tag=['동아리 지원 관련']
)

def get_db():  # db 정보를 fetch 한다음 close하는 함수.
    db = SessionLocal()
    try:
        yield db  # db를 전달함.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# 지원 관련

### 동아리 지원하기 (동아리 지원서 작성)

### (manager) 동아리 지원서 양식 작성하기

### (manager) 동아리 지원자 현황 보기

### (manager) 동아리 지원자의 지원서 보기

### (manager) 동아리 지원 승인하기

### (manager) 동아리 지원 거부하기
