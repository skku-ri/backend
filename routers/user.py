from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users
from routers.auth import get_current_user


router = APIRouter(
    prefix='/user',
    tags=['유저 정보 관련']
)

class UpdateProfileRequest(BaseModel):  # DTO 모델.
    email: str
    nickname: str
    department: str
    student_number: str
    phone_num: str

def get_db():  # db 정보를 fetch 한다음 close하는 함수.
    db = SessionLocal()
    try:
        yield db  # db를 전달함.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# 개인 유저 정보

#
### 프로필 편집 API
#
@router.post("/profile", status_code=status.HTTP_200_OK, summary="프로필 수정 API", description="UpdateProfileRequest에 맞게 데이터를 입력할 경우, email, nickname, department, student_number, phone_num 프로필을 편집하는 API입니다.")
async def update_user(user: user_dependency, db: db_dependency, update_profile_request: UpdateProfileRequest):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is None :
        return "유저 정보가 존재하지 않습니다."

    user_model.email=update_profile_request.email
    user_model.nickname=update_profile_request.nickname
    user_model.department=update_profile_request.department
    user_model.student_number=update_profile_request.student_number
    user_model.phone_num=update_profile_request.phone_num


    db.add(user_model)
    db.commit()

    return "유저 정보를 성공적으로 바꿨습니다."