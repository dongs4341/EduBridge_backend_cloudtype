# 애플리케이션 진입점
# FastAPI 인스턴스 생성, 라우팅, 미들웨어, 이벤트 핸들러 등 설정
from fastapi import FastAPI
from api.user_router import router as user_router
from api.program_router import router as program_router
from api.lecture_request_router import router as lecture_request_router
from app.database import create_tables

# 애플리케이션 시작 시 데이터베이스 테이블 생성
create_tables()

# FastAPI 인스턴스 생성
app = FastAPI()

# 각 라우터 등록
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(program_router, prefix="/programs", tags=["programs"])
app.include_router(
    lecture_request_router, prefix="/lecture-requests", tags=["lecture-requests"]
)


# 루트 URL에 대한 GET 요청 처리
@app.get("/")
def read_root():
    return {"Hello": "World"}
