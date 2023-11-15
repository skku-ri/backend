from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from sqlalchemy import and_

from database import SessionLocal
from models import Club
from routers.auth import get_current_user


router = APIRouter(
    prefix='/club',
    tags=['동아리 검색 및 조회 관련']
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



# 전체 메인 카테고리 조회
@router.get("/main-category", status_code=status.HTTP_200_OK, summary="동아리 메인 카테고리명 조회 API", description="동아리 메인 카테고리들을 확인할 수 있습니다.")
async def read_all_maincategory(db: db_dependency):  # db가 열리는 것에 의존함.
    return db.query(Club.main_category).distinct().all()

# 전체 서브 카테고리 조회
@router.get("/sub-category", status_code=status.HTTP_200_OK, summary="동아리 서브 카테고리명 조회 API", description="동아리 서브 카테고리들을 확인할 수 있습니다.")
async def read_all_subcategory(db: db_dependency):  # db가 열리는 것에 의존함.
    return db.query(Club.sub_category).distinct().all()

# 전체 동아리 조회
@router.get("", status_code=status.HTTP_200_OK, summary="동아리 전체 조회 API", description="등록된 모든 동아리들을 확인할 수 있습니다.")
async def read_all_clubs(db: db_dependency):  # db가 열리는 것에 의존함.
    return db.query(Club).all()

# 모집중인 동아리 조회
@router.get("/recruit", status_code=status.HTTP_200_OK, summary="모집중인 동아리 전체 조회 API", description="모집중인 모든 동아리들을 확인할 수 있습니다.")
async def read_all_recruiting_clubs(db: db_dependency):  # db가 열리는 것에 의존함.
    return db.query(Club).filter(Club.is_recruiting==True).all()

# 동아리 직접검색
@router.get("/search/{clubname}", status_code=status.HTTP_200_OK, summary="동아리 직접검색 API", description="해당 이름(clubname)을 포함하는 모든 동아리명을 출력합니다.")
async def search_name_clubs(db: db_dependency, clubname: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Club).filter(Club.name.contains(clubname)).all()

# 동아리 메인 카테고리별 검색
@router.get("/search/category/{main_category}", status_code=status.HTTP_200_OK, summary="동아리 메인 카테고리별 API", description="해당 메인카테고리(main_category)에 해당하는 모든 동아리를 출력합니다. '인문사회, 학술, 스포츠' 등이 있습니다.")
async def search_maincategory_clubs(db: db_dependency, main_category: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Club).filter(Club.main_category==main_category).all()

# 동아리 카테고리별 검색
@router.get("/search/category/{main_category}/{sub_category}", status_code=status.HTTP_200_OK, summary="동아리 직접검색 API", description="해당 카테고리(main_category, sub_category)에 해당하는 모든 동아리를 출력합니다.\nmain_category에는 '인문사회, 학술, 스포츠' 등이 있고, sub_category에는 '영어, 광고, 한국상경학회' 등이 있습니다.")
async def search_category_clubs(db: db_dependency, main_category: str = Path(), sub_category: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Club).filter(and_(Club.main_category==main_category, Club.sub_category==sub_category)).all()
