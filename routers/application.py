from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_
from starlette import status

from database import SessionLocal
from models import Club, Users, Member, ApplicationForm, Recruit

from routers.auth import get_current_user


router = APIRouter(
    prefix='/application',
    tags=['동아리 지원 관련']
)

def get_db():  # db 정보를 fetch 한다음 close하는 함수.
    db = SessionLocal()
    try:
        yield db  # db를 전달함.
    finally:
        db.close()

class ContentRequest(BaseModel):  # DTO 모델.
    content: str

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# 지원 관련


### 동아리 지원서 양식 보기
@router.get("/form/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 지원서 양식 확인 API", description="해당 동아리의 지원서 양식을 확인합니다.")
async def read_application_form(db: db_dependency, club_id: str=Path()):
    applicationform_model = db.query(ApplicationForm).filter(ApplicationForm.club_id==club_id).first()

    if applicationform_model is None or applicationform_model.content is None:
        return "지원서가 존재하지 않습니다."

    return applicationform_model.content

### 동아리 지원하기 (동아리 지원서 작성)
@router.post("/submit/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 지원 API", description="해당 동아리의 지원서 양식에 맞게 지원서를 작성하고 제출합니다. 각 지원서 질문에 대한 답변은 ,로 구분해주시기 바랍니다. ex) 1번답,2번답,3번답")
async def submit_application_form(db: db_dependency, user: user_dependency, content: ContentRequest, club_id: str=Path()):
    if db.query(Member).filter(and_(Member.club_id==club_id, Member.user_id==user.get("id"))).first() :
        return "이미 해당 동아리의 회원입니다."
    
    recruit_model = Recruit(
        user_id=user.get("id"),
        club_id=club_id,
        content=content.content
    )

    db.add(recruit_model)
    db.commit()

    return "동아리에 지원했습니다."



### (manager) 동아리 모집중 여부 변경하기
@router.put("/recruit/{club_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 모집중 변경 API", description="해당 동아리의 manager가 동아리의 모집중 상태를 변경합니다.")
async def change_recruit(db: db_dependency, user: user_dependency, club_id: str=Path()):
    if authentication_manager(db, user, club_id)==False:
        return "해당 동아리의 운영진이 아닙니다."

    club_model = db.query(Club).filter(Club.id == club_id).first()
    if club_model is None :
        return "동아리 정보가 존재하지 않습니다."
    message = ""

    if club_model.is_recruiting is True:
        club_model.is_recruiting = False
        message = "동아리 회원 모집을 종료했습니다."
    else:
        club_model.is_recruiting = True
        message = "동아리 회원 모집을 시작합니다."


    db.add(club_model)
    db.commit()

    return message

### (manager) 동아리 지원서 양식 작성하기
@router.post("/form/{club_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 지원서 양식 작성 API", description="해당 동아리의 지원서 양식을 작성합니다. content의 내용은 쉼표(,)로 구분해주세요. ex) 1.지원동기가 어떻게돼나요?,2.동아리에 오면 하고 싶은 활동이 있나요?,3.마지막으로 하고싶은 말씀")
async def write_application_form(db: db_dependency, user:user_dependency, content: ContentRequest, club_id: str=Path()):
    if authentication_manager(db, user, club_id)==False:
        return "해당 동아리의 운영진이 아닙니다."

    if db.query(ApplicationForm).filter(ApplicationForm.club_id==club_id).first() is not None:
        return "이미 작성된 양식이 존재합니다."

    applicationform_model = ApplicationForm(
        content=content.content,
        club_id=club_id
    )

    db.add(applicationform_model)
    db.commit()

    return "동아리 지원서 양식을 작성했습니다."

### (manager) 동아리 지원서 양식 삭제하기
@router.delete("/form/{club_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 지원서 양식 삭제 API", description="해당 동아리의 지원서 양식을 삭제합니다.")
async def write_application_form(db: db_dependency, user:user_dependency, content: ContentRequest, club_id: str=Path()):
    if authentication_manager(db, user, club_id)==False:
        return "해당 동아리의 운영진이 아닙니다."

    applicationform_model = db.query(ApplicationForm).filter(ApplicationForm.club_id==club_id).first()

    db.delete(applicationform_model)
    db.commit()

    return "동아리 지원서 양식을 삭제했습니다."

### (manager) 동아리 지원자 현황 및 정보 보기
@router.get("/applicants/{club_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 지원자 현황 및 정보 확인 API", description="해당 동아리에 지원한 사용자들의 정보(지원서)를 확인합니다.")
async def read_applicants(db: db_dependency, user: user_dependency, club_id: str=Path()):
    if authentication_manager(db, user, club_id)==False:
        return "해당 동아리의 운영진이 아닙니다."

    return db.query(Recruit).filter(Recruit.club_id==club_id).all()

### (manager) 동아리 지원자의 지원서 보기

### (manager) 동아리 지원 승인하기
@router.put("/admit/{club_id}/{recruit_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 지원 승인 API", description="해당 동아리에 지원한 사용자를 승인합니다.")
async def admit_applicants(db: db_dependency, user: user_dependency, club_id: str=Path(), recruit_id: str=Path()):
    if authentication_manager(db, user, club_id)==False:
        return "해당 동아리의 운영진이 아닙니다."

    recruit_model = db.query(Recruit).filter(and_(Recruit.id==recruit_id)).first()
    recruit_model.is_approve=True

    member_model = Member(
        user_id=recruit_model.user_id,
        club_id=club_id,
        role="MEMBER"
    )

    db.add(recruit_model)
    db.add(member_model)
    db.commit()

    return "해당 유저는 승인됐습니다."

### (manager) 동아리 지원 거부하기
@router.put("/deny/{club_id}/{recruit_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 지원 거부 API",
            description="해당 동아리에 지원한 사용자를 거부합니다.")
async def admit_applicants(db: db_dependency, user: user_dependency, club_id: str = Path(), recruit_id: str = Path()):
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    recruit_model = db.query(Recruit).filter(and_(Recruit.id == recruit_id)).first()
    recruit_model.is_approve = False

    db.add(recruit_model)
    db.commit()

    return "해당 유저는 거부됐습니다."

### (manager) 가입된 회원 현황 및 정보 보기
@router.get("/members/{club_id}", status_code=status.HTTP_200_OK, summary="[MANAGER] 동아리 멤버 현황 확인 API", description="해당 동아리에 가입한 멤버들의 정보를 확인합니다.")
async def read_members(db: db_dependency, user: user_dependency, club_id: str=Path()):
    if authentication_manager(db, user, club_id)==False:
        return "해당 동아리의 운영진이 아닙니다."

    return db.query(Member).filter(Member.club_id==club_id).all()

### 함수

### 동아리 멤버 추가 함수
def club_add_member(user_id, club_id, db):
    member_model = Member(
      user_id=user_id,
      club_id=club_id,
      role="MEMBER"
    )

    db.add(member_model)
    db.commit()

### 동아리 매니저 확인
def authentication_manager(db, user, club_id):
    member_model = db.query(Member).filter(
        and_(Member.user_id == user.get("id"), Member.club_id == club_id)).first()  # 접근하는 유저 존재 확인.

    if member_model is None:
        return False

    if member_model.role != "MANAGER":
        return False

    return True