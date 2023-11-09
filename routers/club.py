from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal

from routers.auth import get_current_user


router = APIRouter(
    prefix='/club',
    tag=['동아리 관련']
)

def get_db():  # db 정보를 fetch 한다음 close하는 함수.
    db = SessionLocal()
    try:
        yield db  # db를 전달함.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# 동아리 관련

# 전체 동아리 조회

# 모집중인 동아리 조회

# 동아리 직접검색

# 동아리 카테고리별 검색

# 동아리 일정 조회 & 등록 & 삭제

# 동아리 공지사항 조회 & 등록 & 삭제

# 동아리 작품 조회 & 등록 & 삭제

# 동아리 홍보글 조회 & 등록 & 삭제

