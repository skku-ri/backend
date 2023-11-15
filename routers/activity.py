import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from sqlalchemy import and_
from datetime import timedelta, datetime

from starlette.responses import FileResponse

from database import SessionLocal
from models import Club, Schedule, Notice, Artwork
from routers.application import authentication_manager
from routers.auth import get_current_user

router = APIRouter(
    prefix='/activity',
    tags=['동아리 활동 관련']
)


def get_db():  # db 정보를 fetch 한다음 close하는 함수.
    db = SessionLocal()
    try:
        yield db  # db를 전달함.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# 동아리 활동 관련


#
# [ 동아리 일정 관련 ]
#
class ScheduleRequest(BaseModel):
    content: str
    schedule_date: datetime = Field()


# 동아리 일정 조회
@router.get("/schedule/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 일정조회 API",
            description="해당 동아리의 모든 일정을 조회합니다.")
async def read_schedule_club(db: db_dependency, club_id: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Schedule).filter(Schedule.club_id == club_id).all()


# 동아리 일정 등록
@router.post("/schedule/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 일정등록 API",
             description="해당 동아리의 모든 일정을 등록합니다.")
async def post_schedule_club(db: db_dependency, user: user_dependency, schedule_request: ScheduleRequest,
                             club_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    schedule_model = Schedule(
        content=schedule_request.content,
        scheduleDate=schedule_request.schedule_date,
        club_id=club_id
    )

    db.add(schedule_model)
    db.commit()

    return "일정이 추가됐습니다."


# 동아리 일정 삭제
@router.delete("/schedule/{club_id}/{schedule_id}", status_code=status.HTTP_200_OK, summary="동아리 일정 삭제 API",
               description="해당 동아리의 일정 하나를 삭제합니다.")
async def delete_schedule_club(db: db_dependency, user: user_dependency, club_id: str = Path(),
                               schedule_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    schedule_model = db.query(Schedule).filter(Schedule.id == schedule_id).first()

    if schedule_model is None:
        return "해당 일정은 존재하지 않습니다."

    db.delete(schedule_model)
    db.commit()

    return "일정이 삭제됐습니다."


#
# [ 동아리 공지사항 관련 ]
#

class NoticeRequest(BaseModel):
    title: str
    content: str


# 동아리 공지사항 조회

@router.get("/notice/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 공지사항 조회 API",
            description="해당 동아리의 모든 공지사항을 조회합니다.")
async def read_notice_club(db: db_dependency, club_id: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Notice).filter(Notice.club_id == club_id).all()


# 동아리 공지사항 등록
@router.post("/notice/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 공지사항 등록 API",
             description="해당 동아리의 공지사항을 등록합니다.")
async def post_notice_club(db: db_dependency, user: user_dependency, notice_request: NoticeRequest,
                           club_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    notice_model = Notice(
        title=notice_request.title,
        content=notice_request.content,
        club_id=club_id
    )

    db.add(notice_model)
    db.commit()

    return "공지사항이 추가됐습니다."


# 동아리 공지사항 삭제
@router.delete("/notice/{club_id}/{notice_id}", status_code=status.HTTP_200_OK, summary="동아리 공지사항 삭제 API",
               description="해당 동아리의 공지사항 하나를 삭제합니다.")
async def delete_notice_club(db: db_dependency, user: user_dependency, club_id: str = Path(),
                             notice_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    notice_model = db.query(Notice).filter(Notice.id == notice_id).first()

    if notice_model is None:
        return "해당 내용은 존재하지 않습니다."

    db.delete(notice_model)
    db.commit()

    return "공지사항이 삭제됐습니다."


#
# [ 동아리 작품 관련 ]
#

# 동아리 작품 조회
@router.get("/artwork/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 작품 조회 API",
            description="해당 동아리의 모든 작품을 조회합니다.")
async def read_artwork_club(db: db_dependency, club_id: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Artwork).filter(Artwork.club_id == club_id).all()

@router.get("/artwork/image/{imagename}", status_code=status.HTTP_200_OK, summary="동아리 작품 내 이미지 조회 API (사용X)",
            description="서버에 저장된 이미지를 조회합니다. 이때, 서버에 업로드한 이미지 이름을 이용하면 됩니다.")
async def read_artwork_img(imagename: str, db:db_dependency):  # db가 열리는 것에 의존함.
    UPLOAD_DIR = "./artworks"  # 이미지 저장할 서버 경로
    img_path = UPLOAD_DIR + '/' + imagename
    return FileResponse(img_path)

# 동아리 작품 등록
# 이미지와 글을 동시에 보낼땐 Form을 사용하기
@router.post("/artwork/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 작품 등록 API",
             description="해당 동아리의 작품을 등록합니다.")
async def post_artwork_club(db: db_dependency, user: user_dependency, file: UploadFile, title: str = Form(...), content: str = Form(...),
                            club_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    UPLOAD_DIR = "./artworks"  # 이미지 저장할 서버 경로
    image = await file.read()
    filename = f"{str(uuid.uuid4())}.jpg"  # uuid로 유니크한 파일명으로 변경

    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(image)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    artwork_model = Artwork(
        title=title,
        content=content,
        img_path=UPLOAD_DIR + '/' + filename, # TODO : http://127.0.0.1:8000/activity/artwork/image/b86db1c9-78e2-4399-9b24-7b47336d3283.jpg 형식으로 바꾸기!!
        club_id=club_id
    )

    db.add(artwork_model)
    db.commit()

    return "작품이 추가됐습니다."


# 동아리 작품 삭제
@router.delete("/artwork/{club_id}/{artwork_id}", status_code=status.HTTP_200_OK, summary="동아리 작품 삭제 API",
               description="해당 동아리의 작품 하나를 삭제합니다.")
async def delete_artwork_club(db: db_dependency, user: user_dependency, club_id: str = Path(),
                               artwork_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    artwork_model = db.query(Artwork).filter(Artwork.id == artwork_id).first()

    if artwork_model is None:
        return "해당 작품 id 존재하지 않습니다."

    db.delete(artwork_model)
    db.commit()

    return "작품이 삭제됐습니다."

#
# [ 동아리 홍보글 관련 ]
#

class DescriptionRequest(BaseModel):
    content: str

# 동아리 홍보글(설명) 조회
@router.get("/description/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 홍보글(설명) 조회 API",
            description="해당 동아리의 홍보글(설명)을 조회합니다.")
async def read_description_club(db: db_dependency, club_id: str = Path()):  # db가 열리는 것에 의존함.
    return db.query(Club).filter(Club.id == club_id).first().description

# 수정
@router.put("/description/{club_id}", status_code=status.HTTP_200_OK, summary="동아리 홍보글(설명) 수정 API",
            description="해당 동아리의 홍보글(설명)을 수정합니다.")
async def revise_description_club(db: db_dependency, user: user_dependency, description_request: DescriptionRequest, club_id: str = Path()):  # db가 열리는 것에 의존함.
    if authentication_manager(db, user, club_id) == False:
        return "해당 동아리의 운영진이 아닙니다."

    club_model = db.query(Club).filter(Club.id == club_id).first()
    club_model.description = description_request.content

    db.add(club_model)
    db.commit()
    return "홍보글이 수정됐습니다."
