from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)  # 해쉬된 비밀번호
    nickname = Column(String)  # 이름(본명)
    department = Column(String)  # 학과
    student_number = Column(String)  # 학번
    phone_num = Column(String) # 전화번호

class Recruit(Base):
    __tablename__ = 'recruit'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # 지원자
    club_id = Column(Integer, ForeignKey("club.id")) # 지원하려는 동아리
    application_id = Column(Integer, ForeignKey("application.id")) # 지원자의 지원서
    is_approve = Column(Boolean) # 승인 여부

class Member(Base):
    __tablename__ = 'member'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # 멤버
    club_id = Column(Integer, ForeignKey("club.id"))  # 멤버가 속한 동아리
    role = Column(String) # MEMBER 혹은 MANAGER

class Club(Base):
    __tablename__ = 'club'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # 동아리명
    description = Column(String) # 동아리 설명
    locate = Column(String) # 동아리 위치. 학생회관 80401
    logo_img_path = Column(String) # 로고 이미지 경로
    sub_category = Column(String) # 소분류
    main_category = Column(String) # 대분류


class Application(Base):
    __tablename__ = 'application'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String) # 지원서 작성 내용


class ApplicationForm(Base):
    __tablename__ = 'application_form'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String) # 지원서 양식. ['1' : ~ '2' : ~] 로 저장.


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String) # 활동 내용
    scheduleDate = Column(DateTime) # 일정
    club_id = Column(Integer, ForeignKey("club.id"))


class Namecard(Base):
    __tablename__ = 'namecard'

    id = Column(Integer, primary_key=True, index=True)
    img_path = Column(String) # 이미지 경로
    club_id = Column(Integer, ForeignKey("club.id"))


class Notice(Base):
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    club_id = Column(Integer, ForeignKey("club.id"))


class Artwork(Base):
    __tablename__ = 'artwork'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    img_path = Column(String) # 작품 이미지.
    club_id = Column(Integer, ForeignKey("club.id"))

