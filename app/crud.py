# 데이터베이스 CRUD (Create, Read, Update, Delete) 작업을 수행하는 함수 정의
from sqlalchemy.orm import Session, joinedload
from app.models import User as models_User
from app.models import Program as models_Program
from app.models import Request as models_Request
from app.models import ProgramApply as models_ProgramApply
from app.models import RequestApply as models_RequestApply
from app.schemas import (
    UserCreate,
    UserUpdate,
    UserIdFind,
    UserPasswordFind,
    ProgramCreate,
    ProgramUpdate,
    LectureRequestCreate,
    LectureRequestUpdate,
    ProgramApplyCreate,
    RequestApplyCreate,
)
from fastapi import HTTPException
import app.schemas as schemas


# 사용자 ID로 사용자 조회
def get_user_by_id(db: Session, id: str):
    return db.query(models_User).filter(models_User.user_id == id).first()


# 프로그램 상세 조회
def get_program_detail(db: Session, program_id: int, user_id: str):
    program = (
        db.query(models_Program).filter(models_Program.program_id == program_id).first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # 특정 사용자가 특정 프로그램에 신청했는지 확인
    applied_program = (
        db.query(models_ProgramApply)
        .filter(
            models_ProgramApply.program_id == program_id,
            models_ProgramApply.user_id == user_id,
        )
        .first()
    )

    # 신청 여부와 pa_id 설정
    is_applied = applied_program is not None
    pa_id = applied_program.pa_id if is_applied else None

    is_owner = program.user_id == user_id

    program_detail = {
        "program_id": program.program_id,
        "program_name": program.program_name,
        "program_description": program.program_description,
        "program_targetOrganization": program.program_targetOrganization,
        "program_onOffline": program.program_onOffline,
        "program_interruption": program.program_interruption,
        "user_id": program.user_id,
        "program_time": program.program_time,
        "program_maxCapacity": program.program_maxCapacity,
        "program_portfolioUrl": program.program_portfolioUrl,
        "is_applied": is_applied,
        "pa_id": pa_id,  # 신청 시 pa_id 설정
        "is_owner": is_owner,
    }

    return program_detail


# 이메일로 사용자 조회
def get_user_by_email(db: Session, email: str):
    return db.query(models_User).filter(models_User.user_email == email).first()


# 전화번호로 사용자 조회
def get_user_by_phone(db: Session, phoneNumber: str):
    return (
        db.query(models_User)
        .filter(models_User.user_phoneNumber == phoneNumber)
        .first()
    )


# 이름과 이메일로 사용자 조회 (아이디 찾기 기능)
def get_user_by_name_email(db: Session, user_idFind: UserIdFind):
    return (
        db.query(models_User)
        .filter(
            models_User.user_name == user_idFind.user_name,
            models_User.user_email == user_idFind.user_email,
        )
        .first()
    )


# 사용자 ID와 이메일로 사용자 조회 (비밀번호 찾기 기능)
def get_user_by_id_email(db: Session, user_passwordFind: UserPasswordFind):
    return (
        db.query(models_User)
        .filter(
            models_User.user_id == user_passwordFind.user_id,
            models_User.user_email == user_passwordFind.user_email,
        )
        .first()
    )


# 사용자 비밀번호 업데이트
def update_user_password(db: Session, user: models_User, new_password: str):
    user.user_password = models_User.get_password_hash(new_password)
    db.commit()
    return user


# 프로그램 ID로 프로그램 조회
def get_program_by_id(db: Session, program_id: int):
    return (
        db.query(models_Program).filter(models_Program.program_id == program_id).first()
    )


# 강의의뢰 ID로 강의의뢰 조회
def get_lecture_request_by_id(db: Session, request_id: int):
    return (
        db.query(models_Request).filter(models_Request.request_id == request_id).first()
    )


# 강의의뢰 상세 조회
def get_lecture_request_detail(db: Session, request_id: int, user_id: str):
    request = (
        db.query(models_Request).filter(models_Request.request_id == request_id).first()
    )
    if not request:
        raise HTTPException(status_code=404, detail="Lecture request not found")

    # 특정 사용자가 특정 강의 의뢰에 지원했는지 확인
    applied_request = (
        db.query(models_RequestApply)
        .filter(
            models_RequestApply.request_id == request_id,
            models_RequestApply.user_id == user_id,
        )
        .first()
    )

    is_applied = applied_request is not None
    ra_id = applied_request.ra_id if is_applied else None

    print(f"Applied Request: {applied_request}")  # 디버깅 출력
    print(f"is_applied: {is_applied}, ra_id: {ra_id}")  # 디버깅 출력

    is_owner = request.user_id == user_id

    request_detail = {
        "request_subject": request.request_subject,
        "request_content": request.request_content,
        "request_targetAudience": request.request_targetAudience,
        "request_date": request.request_date,
        "request_startTime": request.request_startTime,
        "request_endTime": request.request_endTime,
        "request_qualifications": request.request_qualifications,
        "request_onOffline": request.request_onOffline,
        "request_place": request.request_place,
        "request_detailedAddress": request.request_detailedAddress,
        "request_audienceCount": request.request_audienceCount,
        "request_lectureFee": request.request_lectureFee,
        "request_completed": request.request_completed,
        "request_id": request.request_id,
        "user_id": request.user_id,
        "is_applied": is_applied,
        "ra_id": ra_id,  # 지원 시 ra_id 설정
        "is_owner": is_owner,
    }

    return request_detail


# 사용자 ID에 따른 프로그램 목록 조회
def get_programs_by_user_id(db: Session, user_id: str):
    return db.query(models_Program).filter(models_Program.user_id == user_id).all()


# 사용자 ID에 따른 강의 의뢰 목록 조회
def get_lecture_requests_by_user_id(db: Session, user_id: str):
    return db.query(models_Request).filter(models_Request.user_id == user_id).all()


# 사용자 생성 (회원가입)
def create_user(db: Session, user: UserCreate):
    hashed_password = models_User.get_password_hash(user.user_password)  # 비밀번호 해싱
    db_user = models_User(
        user_id=user.user_id,
        user_password=hashed_password,  # 비밀번호는 해싱되어 저장
        user_name=user.user_name,
        user_phoneNumber=user.user_phoneNumber,
        user_email=user.user_email,
        user_type=user.user_type,
        user_registrationDate=models_User.get_kst_now(),  # KST 시각으로 설정
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 사용자 정보 수정
def update_user(db: Session, user_id: str, user: UserUpdate):
    db_user = get_user_by_id(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.dict(exclude_unset=True)
    # 비밀번호가 제공되었다면 해싱 처리
    if "user_password" in user_data:
        user_data["user_password"] = models_User.get_password_hash(
            user_data["user_password"]
        )

    for key, value in user_data.items():
        setattr(db_user, key, value)
    db_user.user_update = models_User.get_kst_now()  # 사용자 정보 수정 시각 업데이트
    db.commit()
    return db_user


# 사용자 인증 (로그인)
def authenticate_user(db: Session, user_id: str, password: str):
    # 사용자 조회
    db_user = get_user_by_id(db, id=user_id)
    # 비밀번호 검증
    if db_user and db_user.verify_password(password):
        return db_user
    return None


# 사용자 삭제 (보류)
def delete_user(db: Session, user_id: str):
    db_user = get_user_by_id(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db_user


# 프로그램 등록
def create_program(db: Session, program: ProgramCreate, user_id: str):
    db_program = models_Program(
        program_name=program.program_name,
        program_description=program.program_description,
        program_time=program.program_time,
        program_targetOrganization=program.program_targetOrganization,
        program_onOffline=program.program_onOffline,
        program_maxCapacity=program.program_maxCapacity,
        program_portfolioUrl=(
            str(program.program_portfolioUrl) if program.program_portfolioUrl else None
        ),
        user_id=user_id,
        program_interruption=False,
    )
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


# 프로그램 수정
def update_program(db: Session, program_id: int, program: ProgramUpdate):
    db_program = get_program_by_id(db, program_id)
    if not db_program:
        return None

    update_data = program.dict(exclude_unset=True)

    # program_portfolioUrl 필드가 있다면 문자열로 변환
    if (
        "program_portfolioUrl" in update_data
        and update_data["program_portfolioUrl"] is not None
    ):
        update_data["program_portfolioUrl"] = str(update_data["program_portfolioUrl"])

    for key, value in update_data.items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program


# 프로그램 삭제
def delete_program(db: Session, program_id: int) -> bool:
    db_program = (
        db.query(models_Program).filter(models_Program.program_id == program_id).first()
    )
    if not db_program:
        return False

    # 신청자가 있는지 확인
    applicants = (
        db.query(models_ProgramApply)
        .filter(models_ProgramApply.program_id == program_id)
        .all()
    )
    if applicants:
        raise HTTPException(
            status_code=400, detail="Cannot delete program with applicants"
        )

    db.delete(db_program)
    db.commit()
    return True  # 삭제 성공 시 True 반환


# 프로그램 중단
def interrupt_program(db: Session, program_id: int):
    db_program = get_program_by_id(db, program_id)
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    db_program.program_interruption = True
    db.commit()
    db.refresh(db_program)
    return db_program


# 프로그램 검색
def search_programs(db: Session, search_query: str):
    return (
        db.query(models_Program)
        .filter(
            models_Program.program_name.contains(search_query)
            | models_Program.program_description.contains(search_query)
        )
        .all()
    )


# 강의 의뢰 등록
def create_lecture_request(db: Session, request: LectureRequestCreate, user_id: str):
    db_request = models_Request(
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
        user_id=user_id,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


# 강의 의뢰 수정
def update_lecture_request(db: Session, request_id: int, request: LectureRequestUpdate):
    db_request = get_lecture_request_by_id(db, request_id)
    if not db_request:
        return None

    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_request, key, value)

    db.commit()
    db.refresh(db_request)
    return db_request


# 강의의뢰 삭제
def delete_lecture_request(db: Session, request_id: int) -> bool:
    db_request = get_lecture_request_by_id(db, request_id)
    if not db_request:
        return False

    # 지원자가 있는지 확인
    applicants = (
        db.query(models_RequestApply)
        .filter(models_RequestApply.request_id == request_id)
        .all()
    )
    if applicants:
        raise HTTPException(
            status_code=400, detail="Cannot delete lecture request with applicants"
        )

    db.delete(db_request)
    db.commit()
    return True


# 강의 의뢰 검색
def search_lecture_requests(db: Session, search_query: str):
    return (
        db.query(models_Request)
        .filter(
            models_Request.request_subject.contains(search_query)
            | models_Request.request_content.contains(search_query)
        )
        .all()
    )


# 모든 프로그램 조회
def get_all_programs(db: Session):
    return db.query(models_Program).all()


# 모든 강의 의뢰 조회
def get_all_lecture_requests(db: Session):
    return db.query(models_Request).all()


# 프로그램 신청 생성
def create_program_apply(db: Session, program_apply: ProgramApplyCreate, user_id: str):
    # program_name, user_name, user_phoneNumber를 채우기 위해 필요한 데이터 가져오기
    program = get_program_by_id(db, program_apply.program_id)
    user = get_user_by_id(db, user_id)

    if not program or not user:
        raise HTTPException(status_code=404, detail="Program or User not found")

    db_program_apply = models_ProgramApply(
        program_id=program_apply.program_id,
        user_id=user.user_id,
        pa_date=program_apply.pa_date,
        pa_startTime=program_apply.pa_startTime,
        pa_endTime=program_apply.pa_endTime,
        pa_onOffline=program_apply.pa_onOffline,
        pa_address=program_apply.pa_address,
        pa_detailedAddress=program_apply.pa_detailedAddress,
        pa_targetAudience=program_apply.pa_targetAudience,
        pa_personnel=program_apply.pa_personnel,  # 진행 인원 수
        pa_status="대기",  # 상태를 명시적으로 "대기"로 설정
        pa_lectureFee=program_apply.pa_lectureFee,
        program_name=program.program_name,  # 트리거로 채워질 프로그램명
        user_name=user.user_name,  # 트리거로 채워질 사용자 이름
        user_phoneNumber=user.user_phoneNumber,  # 트리거로 채워질 사용자 전화번호
    )
    db.add(db_program_apply)
    db.commit()
    db.refresh(db_program_apply)
    return db_program_apply


# 강의 의뢰 지원 생성
def create_request_apply(db: Session, request_apply: RequestApplyCreate, user_id: str):
    # request_subject, user_name, user_email, user_phoneNumber를 채우기 위해 필요한 데이터 가져오기
    request = get_lecture_request_by_id(db, request_apply.request_id)
    user = get_user_by_id(db, user_id)

    if not request or not user:
        raise HTTPException(status_code=404, detail="Request or User not found")

    db_request_apply = models_RequestApply(
        request_id=request_apply.request_id,
        user_id=user.user_id,
        ra_status="대기",  # 상태를 명시적으로 "대기"로 설정
        ra_dateOfBirth=request_apply.ra_dateOfBirth,
        ra_gender=request_apply.ra_gender,
        request_subject=request.request_subject,  # 트리거로 채워질 강의 의뢰 제목
        user_name=user.user_name,  # 트리거로 채워질 사용자 이름
        user_email=user.user_email,  # 트리거로 채워질 사용자 이메일
        user_phoneNumber=user.user_phoneNumber,  # 트리거로 채워질 사용자 전화번호
    )
    db.add(db_request_apply)
    db.commit()
    db.refresh(db_request_apply)
    return db_request_apply


# 프로그램 신청 조회
def get_program_apply(db: Session, pa_id: int):
    return (
        db.query(models_ProgramApply)
        .options(
            joinedload(models_ProgramApply.program),
            joinedload(models_ProgramApply.user),
        )
        .filter(models_ProgramApply.pa_id == pa_id)
        .first()
    )


# 강의 의뢰 지원 조회
def get_request_apply(db: Session, ra_id: int):
    return (
        db.query(models_RequestApply)
        .options(
            joinedload(models_RequestApply.request),
            joinedload(models_RequestApply.user),
        )
        .filter(models_RequestApply.ra_id == ra_id)
        .first()
    )


# 모든 프로그램 신청 조회
def get_all_program_applies(db: Session):
    return db.query(models_ProgramApply).all()


# 모든 강의 의뢰 지원 조회
def get_all_request_applies(db: Session):
    return db.query(models_RequestApply).all()


# 강사가 지원한 강의 의뢰 조회
def get_request_applies_by_user_id(db: Session, user_id: str):
    return (
        db.query(models_RequestApply)
        .filter(models_RequestApply.user_id == user_id)
        .all()
    )


# 강의 의뢰자가 신청한 프로그램 조회
def get_program_applies_by_user_id(db: Session, user_id: str):
    return (
        db.query(models_ProgramApply)
        .filter(models_ProgramApply.user_id == user_id)
        .all()
    )


# 강의 의뢰 지원 내역 수정
def update_request_apply(db: Session, ra_id: int, request_apply: RequestApplyCreate):
    db_request_apply = get_request_apply(db, ra_id)
    if not db_request_apply:
        raise HTTPException(status_code=404, detail="Request apply not found")

    update_data = request_apply.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_request_apply, key, value)

    db.commit()
    db.refresh(db_request_apply)
    return db_request_apply


# 프로그램 신청 내역 수정
def update_program_apply(db: Session, pa_id: int, program_apply: ProgramApplyCreate):
    db_program_apply = get_program_apply(db, pa_id)
    if not db_program_apply:
        raise HTTPException(status_code=404, detail="Program apply not found")

    update_data = program_apply.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_program_apply, key, value)

    db.commit()
    db.refresh(db_program_apply)
    return db_program_apply


# 강의 의뢰 지원 내역 삭제
def delete_request_apply(db: Session, ra_id: int):
    db_request_apply = get_request_apply(db, ra_id)
    if not db_request_apply:
        raise HTTPException(status_code=404, detail="Request apply not found")

    db.delete(db_request_apply)
    db.commit()
    return True


# 프로그램 신청 내역 삭제
def delete_program_apply(db: Session, pa_id: int):
    db_program_apply = get_program_apply(db, pa_id)
    if not db_program_apply:
        raise HTTPException(status_code=404, detail="Program apply not found")

    db.delete(db_program_apply)
    db.commit()
    return True


# 강의의뢰 지원 수락 시 상태 변경
def accept_request_apply(db: Session, ra_id: int):
    db_request_apply = get_request_apply(db, ra_id)
    if not db_request_apply:
        raise HTTPException(status_code=404, detail="Request apply not found")

    db_request_apply.ra_status = "수락"
    db.commit()
    db.refresh(db_request_apply)
    return db_request_apply


# 강의의뢰 지원 거절 시 상태 변경
def reject_request_apply(db: Session, ra_id: int):
    db_request_apply = get_request_apply(db, ra_id)
    if not db_request_apply:
        raise HTTPException(status_code=404, detail="Request apply not found")

    db_request_apply.ra_status = "거절"
    db.commit()
    db.refresh(db_request_apply)
    return db_request_apply


# 프로그램 신청 수락 시 상태 변경
def accept_program_apply(db: Session, pa_id: int):
    db_program_apply = get_program_apply(db, pa_id)
    if not db_program_apply:
        raise HTTPException(status_code=404, detail="Program apply not found")

    db_program_apply.pa_status = "수락"
    db.commit()
    db.refresh(db_program_apply)
    return db_program_apply


# 프로그램 신청 거절 시 상태 변경
def reject_program_apply(db: Session, pa_id: int):
    db_program_apply = get_program_apply(db, pa_id)
    if not db_program_apply:
        raise HTTPException(status_code=404, detail="Program apply not found")

    db_program_apply.pa_status = "거절"
    db.commit()
    db.refresh(db_program_apply)
    return db_program_apply


# 강사가 등록한 프로그램에 신청한 강의 의뢰자 목록 조회
def get_program_applies_by_program_id(db: Session, program_id: int):
    applies = (
        db.query(models_ProgramApply)
        .filter(models_ProgramApply.program_id == program_id)
        .options(joinedload(models_ProgramApply.program))
        .all()
    )
    results = []
    for apply in applies:
        matching_status = "매칭 완료" if apply.pa_status == "수락" else "매칭 실패" if apply.pa_status == "거절" else "대기"
        result = schemas.ProgramApply(
            program_id=apply.program_id,
            pa_id=apply.pa_id,
            program_name=apply.program_name,
            user_name=apply.user_name,
            user_phoneNumber=apply.user_phoneNumber,
            pa_lectureFee=apply.pa_lectureFee,
            pa_date=apply.pa_date,
            pa_startTime=apply.pa_startTime,
            pa_endTime=apply.pa_endTime,
            pa_onOffline=apply.pa_onOffline,
            pa_address=apply.pa_address,
            pa_detailedAddress=apply.pa_detailedAddress,
            pa_targetAudience=apply.pa_targetAudience,
            pa_personnel=apply.pa_personnel,
            matching_status=matching_status
        )
        results.append(result)
    return results


# 강의 의뢰자가 등록한 강의 의뢰에 지원한 강사 목록 조회
def get_request_applies_by_request_id(db: Session, request_id: int):
    applies = (
        db.query(models_RequestApply)
        .filter(models_RequestApply.request_id == request_id)
        .options(joinedload(models_RequestApply.request))
        .all()
    )
    results = []
    for apply in applies:
        matching_status = "매칭 완료" if apply.ra_status == "수락" else "매칭 실패" if apply.ra_status == "거절" else "대기"
        result = schemas.RequestApply(
            request_id=apply.request_id,
            ra_id=apply.ra_id,
            request_subject=apply.request_subject,
            user_name=apply.user_name,
            user_email=apply.user_email,
            user_phoneNumber=apply.user_phoneNumber,
            ra_dateOfBirth=apply.ra_dateOfBirth,
            ra_gender=apply.ra_gender,
            matching_status=matching_status
        )
        results.append(result)
    return results