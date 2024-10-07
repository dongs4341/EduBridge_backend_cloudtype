from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.crud as crud
import app.schemas as schemas
import app.auth  as auth
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 사용자 생성 (회원가입)
@router.post("/signup", response_model=schemas.User, summary="회원가입")
def create_user_route(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user_id = crud.get_user_by_id(db, id=user.user_id)
        db_user_email = crud.get_user_by_email(db, email=user.user_email)
        db_user_phone = crud.get_user_by_phone(db, phoneNumber=user.user_phoneNumber)
        if db_user_id or db_user_email or db_user_phone:
            raise HTTPException(status_code=400, detail="User already registered")
        return crud.create_user(db=db, user=user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 사용자 정보 수정
@router.put("/users-update/{user_id}", response_model=schemas.User, summary="사용자 정보 수정")
def update_user_route(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db=db, user_id=user_id, user=user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# 사용자 정보 조회
@router.get("/users/{user_id}", response_model=schemas.User, summary="사용자 정보 조회")
def read_user_route(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 로그인
@router.post("/login", summary="로그인")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect user ID or password")
    access_token = auth.create_access_token(user.user_id)
    refresh_token = auth.create_refresh_token(user.user_id)
    return {"access_token": access_token, "refresh_token": refresh_token, "user_id": user.user_id, "user_type": user.user_type}

# 아이디 찾기
@router.post("/find-userid", response_model=str, summary="아이디 찾기")
def find_userid(user_idFind: schemas.UserIdFind, db: Session = Depends(get_db)):
    user = crud.get_user_by_name_email(db, user_idFind)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    masked_username = user.user_id[:-3] + '***'
    return masked_username

# 비밀번호 찾기
@router.post("/find-userpassword", response_model=str, summary="비밀번호 찾기")
def find_userpassword(user_passwordFind: schemas.UserPasswordFind, db: Session = Depends(get_db)):
    user = crud.get_user_by_id_email(db, user_passwordFind)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    temp_password = auth.generate_temp_password()
    user = crud.update_user_password(db, user, temp_password)
    return temp_password

# 중복검사 버튼
@router.get("/check-userid/{user_id}", summary="사용자 ID 중복 검사")
def check_username(user_id: str, db: Session = Depends(get_db)):
    if crud.get_user_by_id(db, id=user_id):
        return {"available": False}
    return {"available": True}

@router.get("/check-email/{email}", summary="사용자 email 중복 검사")
def check_email(email: str, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email=email):
        return {"available": False}
    return {"available": True}

@router.get("/check-phone/{phone_number}", summary="사용자 휴대전화번호 중복 검사")
def check_phone_number(phoneNumber: str, db: Session = Depends(get_db)):
    if crud.get_user_by_phone(db, phoneNumber=phoneNumber):
        return {"available": False}
    return {"available": True}

# 강사가 지원한 강의 의뢰 조회
@router.get("/my-request-applies", response_model=List[schemas.RequestApply], summary="[강사]가 지원한 강의의뢰 지원정보 조회", description="현재 사용자가 [강사]이고 지원한 강의의뢰를 조회 후 나열")
def get_my_request_applies(current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "강사":
        raise HTTPException(status_code=403, detail="Only instructors can view their request applies.")
    return crud.get_request_applies_by_user_id(db, current_user.user_id)

# 강의 의뢰자가 신청한 프로그램 조회
@router.get("/my-program-applies", response_model=List[schemas.ProgramApply], summary="[강의 의뢰자]가 신청한 프로그램 신청정보 조회", description="현재 사용자가 [강의 의뢰자]이고 신청한 프로그램을 조회 후 나열")
def get_my_program_applies(current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "강의 의뢰자":
        raise HTTPException(status_code=403, detail="Only requesters can view their program applies.")
    return crud.get_program_applies_by_user_id(db, current_user.user_id)

# 현재 사용자(강사)가 등록한 프로그램 목록 조회
@router.get("/my-programs", response_model=List[schemas.ProgramSchema], summary="[강사]가 등록한 프로그램 조회", description="현재 사용자가 [강사]이고 본인이 등록한 프로그램을 조회 후 나열")
def get_my_programs(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    programs = crud.get_programs_by_user_id(db, user_id=current_user.user_id)
    if not programs:
        raise HTTPException(status_code=404, detail="No programs found.")
    return programs

# 현재 사용자(강의 의뢰자)가 등록한 강의 의뢰 목록 조회
@router.get("/my-requests", response_model=List[schemas.LectureRequestSchema], summary="[강의 의뢰자]가 등록한 강의의뢰 조회", description="현재 사용자가 [강의 의뢰자]이고 본인이 등록한 강의의뢰를 조회 후 나열")
def get_my_requests(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    requests = crud.get_lecture_requests_by_user_id(db, user_id=current_user.user_id)
    if not requests:
        raise HTTPException(status_code=404, detail="No lecture requests found.")
    return requests

# 강사가 지원한 강의 의뢰 내역 조회 (매칭 상태 포함)
@router.get("/my-request-applies/status", response_model=List[schemas.RequestApplyWithStatus], summary="강의의뢰 지원 내역 조회")
def get_my_request_applies_status(current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "강사":
        raise HTTPException(status_code=403, detail="Only instructors can view their request applies.")
    applies = crud.get_request_applies_by_user_id(db, current_user.user_id)
    results = []
    for apply in applies:
        matching_status = "매칭 완료" if apply.ra_status == "수락" else "매칭 실패" if apply.ra_status == "거절" else "대기"
        request = crud.get_lecture_request_by_id(db, apply.request_id)
        result = schemas.RequestApplyWithStatus(
            request_id=request.request_id,
            ra_id=apply.ra_id,
            request_subject=request.request_subject,
            request_content=request.request_content,
            request_targetAudience=request.request_targetAudience,
            request_date=request.request_date,
            request_startTime=request.request_startTime,
            request_endTime=request.request_endTime,
            request_qualifications=request.request_qualifications,
            request_onOffline=request.request_onOffline,
            request_place=request.request_place,
            request_detailedAddress=request.request_detailedAddress,
            request_audienceCount=request.request_audienceCount,
            request_lectureFee=request.request_lectureFee,
            matching_status=matching_status
        )
        results.append(result)
    return results

# 강의 의뢰자가 프로그램 신청 내역 조회 (매칭 상태 포함)
@router.get("/my-program-applies/status", response_model=List[schemas.ProgramApplyWithStatus], summary="프로그램 신청 내역 조회")
def get_my_program_applies_status(current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.user_type != "강의 의뢰자":
        raise HTTPException(status_code=403, detail="Only requesters can view their program applies.")
    applies = crud.get_program_applies_by_user_id(db, current_user.user_id)
    results = []
    for apply in applies:
        matching_status = "매칭 완료" if apply.pa_status == "수락" else "매칭 실패" if apply.pa_status == "거절" else "대기"
        program = crud.get_program_by_id(db, apply.program_id)
        result = schemas.ProgramApplyWithStatus(
            program_id=program.program_id,
            pa_id=apply.pa_id,
            program_name=program.program_name,
            program_description=program.program_description,
            program_time=program.program_time,
            program_targetOrganization=program.program_targetOrganization,
            program_onOffline=program.program_onOffline,
            program_maxCapacity=program.program_maxCapacity,
            program_portfolioUrl=program.program_portfolioUrl,
            matching_status=matching_status
        )
        results.append(result)
    return results
