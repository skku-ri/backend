from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends  # main에서 router할 수 있게 함.
from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Users
from database import SessionLocal
from passlib.context import CryptContext
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # OAUTH2 비번
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',  # 접두사
    tags=['유저 계정 관련']  # 타이틀.
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')  # hash 알고리즘
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# openssl rand -hex 32로 생성함
SECRET_KEY = '72589414265e6e6c5997672c6811264f60f6f3a70cce0b4cec4f842a804d2c72'
ALGORITHM = 'HS256'


class CreateUserRequest(BaseModel):  # DTO 모델.
    email: str
    password: str
    nickname: str
    department: str
    student_number: str
    phone_num: str


class Token(BaseModel):  # 토큰용
    access_token: str
    token_type: str


def get_db():  # db 정보를 fetch 한다음 close하는 함수.
    db = SessionLocal()
    try:
        yield db  # db를 전달함.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# 유저 인증 함수
def authenticate_user(email: str, password: str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):  # 해시값 기반으로 비밀번호 비교
        return False
    return user


# JWT 토큰 생성 함수
def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': email, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


#
### 유저 생성 API
#
@router.post("/create", status_code=status.HTTP_201_CREATED, summary="신규 유저 등록(회원가입) API", description="유저 정보를 입력할 경우, 유저를 생성하여 DB에 저장하는 API입니다.")
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user_model = db.query(Users).filter(Users.email == create_user_request.email).first() # 유저 존재 확인

    if user_model :
        return "이메일이 중복되는 유저가 존재합니다."

    create_user_model = Users(
        email=create_user_request.email,
        nickname=create_user_request.nickname,
        department=create_user_request.department,
        hashed_password=bcrypt_context.hash(create_user_request.password),  # hash
        student_number=create_user_request.student_number,
        phone_num=create_user_request.phone_num
    )

    db.add(create_user_model)
    db.commit()

    return create_user_request.nickname + " 유저 생성 완료"


# JWT 확인하고 유저 가져오는 함수
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')  # username과 같음, sub
        user_id: int = payload.get('id')  # id
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='잘못된 유저 정보입니다.')

        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='잘못된 유저 정보입니다.')


#
### OAUTH2 FORM 기반으로 로그인 인증 API
#
@router.post("/token", response_model=Token, summary="로그인 인증 API", description="OAUTH2 기반입니다. username에 email을, password에 password를 입력할 경우, JWT 토큰을 리턴합니다. 해당 토큰은 header의 authorization 속성에서 사용할 수 있습니다.")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # 오직 사용자가 입력할 값은 username과 비밀번호가 전부.
    # 사용자 이름 기반으로 유저 가져오기
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return 'Failed Authentication'

    token = create_access_token(user.email, user.id, timedelta(minutes=60))

    return {'access_token': token, 'token_type': 'bearer'}
