import secrets, string  # 무작위 문자열 생성을 위한 모듈
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials   # OAuth2 토큰 생성을 위한 FastAPI 보안 유틸리티
from jose import jwt, JWTError  # JWT 토큰 생성 및 검증을 위한 라이브러리
from datetime import datetime, timedelta    # 시간 계산을 위한 모듈
from typing import Union, Any   # 타입 힌팅을 위한 모듈 //변수나 함수가 어떤 종류의 데이터를 처리해야 하는지 미리 알려주는 도구
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import app.crud as crud
from app.database import SessionLocal

# 토큰 발급 URL을 지정하는 OAuth2PasswordBearer 객체 생성 //클라이언트에서 인증 요청을 보낼 때 사용할 URL을 설정함
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT 생성에 사용될 서명 알고리즘과 비밀 키 설정
SECRET_KEY = secrets.token_urlsafe(64)  # 토큰을 서명할 때 사용할 비밀키 //64바이트 길이의 안전한 URL과 파일 이름에 적합한 키 생성
ALGORITHM = "HS256"     # 서명 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30    # Access Token의 만료 시간 (분 단위)
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Refresh Token의 만료 시간 (분 단위, 일주일)


# [로그인] Access Token 생성     //사용자 인증 후, 사용자의 정보와 함께 토큰 발행
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:        # 만료 시간 설정 // expires_delta가 없으면 기본값 사용, 제공되면 그 값 사용 
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, 'sub': str(subject)} # 토큰에 포함될 내용을 딕셔너리로 준비
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)   # JWT 생성 및 인코딩
    return encoded_jwt

# [로그인] Refresh Token 생성    //장기간 로그인 상태를 유지하기 위해 사용
def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:        # 만료 시간 설정 //expires_delta가 없으면 기본값 사용, 제공되면 그 값 사용 
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, 'sub': str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

# Bearer 스키마 선언
bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        # JWT 토큰 디코딩 및 사용자 ID 추출
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 데이터베이스에서 사용자 정보 가져오기
    db: Session = SessionLocal()
    user = crud.get_user_by_id(db, id=user_id)
    db.close()

    if user is None:
        raise credentials_exception
    return user

# [비밀번호 찾기] 임시비밀번호 생성 
def generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits  # 사용할 문자 집합
    # 지정된 길이만큼 무작위 문자를 선택하여 임시 비밀번호 생성
    return ''.join(secrets.choice(alphabet) for i in range(length))