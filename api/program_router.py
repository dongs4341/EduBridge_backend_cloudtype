from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.crud as crud
import app.schemas as schemas
import app.auth as auth
from app.database import SessionLocal
from typing import List
from app.utils import shorten_text  # 유틸리티 함수 가져오기

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 프로그램 등록
@router.post(
    "/",
    response_model=schemas.ProgramSchema,
    status_code=status.HTTP_201_CREATED,
    summary="프로그램 등록",
)
def create_program_route(
    program: schemas.ProgramCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.user_type != "강사":
        raise HTTPException(
            status_code=403, detail="Only instructors can create programs."
        )
    return crud.create_program(db, program, current_user.user_id)


# 프로그램 수정
@router.put(
    "/{program_id}", response_model=schemas.ProgramSchema, summary="프로그램 수정"
)
def update_program_route(
    program_id: int,
    program: schemas.ProgramUpdate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program = crud.get_program_by_id(db, program_id)
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")
    if db_program.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Only the program creator can modify this program."
        )
    return crud.update_program(db, program_id, program)


# 프로그램 삭제
@router.delete("/{program_id}", response_model=dict, summary="프로그램 삭제")
def delete_program_route(
    program_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program = crud.get_program_by_id(db, program_id)
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")
    if db_program.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="Only the program creator can delete this program."
        )
    try:
        if not crud.delete_program(db, program_id):
            raise HTTPException(status_code=404, detail="Unable to delete program")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return {"detail": "Program successfully deleted"}


# 프로그램 중단
@router.post(
    "/{program_id}/interrupt",
    response_model=schemas.ProgramDetail,
    summary="프로그램 중단",
)
def interrupt_program_route(
    program_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program = crud.get_program_by_id(db, program_id)
    if db_program.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can only interrupt your own programs."
        )
    return crud.interrupt_program(db, program_id)


# 프로그램 검색
@router.post(
    "/search", response_model=List[schemas.ProgramSchema], summary="프로그램 검색"
)
def search_programs(search_query: str, db: Session = Depends(get_db)):
    programs = crud.search_programs(db, search_query=search_query)
    if not programs:
        raise HTTPException(status_code=404, detail="program not found")
    summarized_programs = []
    for program in programs:
        summarized_program = {
            "program_name": program.program_name,
            "program_description": shorten_text(program.program_description, 50),
            "program_targetOrganization": shorten_text(
                program.program_targetOrganization, 10
            ),
            "program_onOffline": program.program_onOffline,
            "program_interruption": program.program_interruption,
            "program_id": program.program_id,
            "user_id": program.user_id,
        }
        summarized_programs.append(summarized_program)
    return summarized_programs


# 모든 프로그램 조회
@router.get(
    "/list", response_model=List[schemas.ProgramSchema], summary="모든 프로그램 조회"
)
def get_programs_summary(db: Session = Depends(get_db)):
    programs = crud.get_all_programs(db)
    if not programs:
        raise HTTPException(status_code=404, detail="No programs found.")
    summarized_programs = []
    for program in programs:
        summarized_program = {
            "program_name": program.program_name,
            "program_description": shorten_text(program.program_description, 50),
            "program_targetOrganization": shorten_text(
                program.program_targetOrganization, 10
            ),
            "program_onOffline": program.program_onOffline,
            "program_interruption": program.program_interruption,
            "program_id": program.program_id,
            "user_id": program.user_id,
            "program_time": program.program_time,
            "program_maxCapacity": program.program_maxCapacity,
            "program_portfolioUrl": program.program_portfolioUrl,
        }
        summarized_programs.append(summarized_program)
    return summarized_programs


# 프로그램 상세 조회 시 is_applied 필드를 포함한 응답을 반환
@router.get(
    "/{program_id}",
    # response_model=schemas.ProgramDetail,
    # summary="프로그램 상세 조회"
)
def get_program_detail_route(
    program_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    program_detail = crud.get_program_detail(db, program_id, current_user.user_id)
    if not program_detail:
        raise HTTPException(status_code=404, detail="Program not found")

    return program_detail


# 프로그램 신청 수락
@router.post(
    "/program-applies/{pa_id}/accept",
    response_model=schemas.ProgramApply,
    summary="프로그램 신청 수락",
)
def accept_program_apply_route(
    pa_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program_apply = crud.get_program_apply(db, pa_id)
    if not db_program_apply:  # None 체크 추가
        raise HTTPException(status_code=404, detail="Program apply not found")
    if db_program_apply.program.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="프로그램 신청 수락은 본인의 프로그램에만 가능합니다.",
        )

    return crud.accept_program_apply(db, pa_id)


# 프로그램 신청 거절
@router.post(
    "/program-applies/{pa_id}/reject",
    response_model=schemas.ProgramApply,
    summary="프로그램 신청 거절",
)
def reject_program_apply_route(
    pa_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program_apply = crud.get_program_apply(db, pa_id)
    if not db_program_apply:  # None 체크 추가
        raise HTTPException(status_code=404, detail="Program apply not found")
    if db_program_apply.program.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="프로그램 신청 거절은 본인의 프로그램에만 가능합니다.",
        )

    return crud.reject_program_apply(db, pa_id)


# 프로그램 신청 등록
@router.post(
    "/program_applies",
    response_model=schemas.ProgramApply,
    status_code=status.HTTP_201_CREATED,
    summary="프로그램 신청",
)
def create_program_apply_route(
    program_apply: schemas.ProgramApplyCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    print(f"Current User ID: {current_user.user_id}")  # 디버깅 출력
    return crud.create_program_apply(
        db=db, program_apply=program_apply, user_id=current_user.user_id
    )


# 프로그램 신청 내역 수정
@router.put(
    "/program-applies/{pa_id}",
    response_model=schemas.ProgramApply,
    summary="특정 프로그램 신청 내역 수정",
    description="프로그램 신청 시 작성하였던 내역 수정",
)
def update_program_apply_route(
    pa_id: int,
    program_apply: schemas.ProgramApplyCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program_apply = crud.get_program_apply(db, pa_id)
    if db_program_apply.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can only modify your own program applies."
        )
    return crud.update_program_apply(db, pa_id, program_apply)


# 프로그램 신청 취소
@router.delete(
    "/program-applies/{pa_id}",
    response_model=dict,
    summary="특정 프로그램 신청 내역 삭제",
    description="프로그램 신청 시 작성하였던 내역 삭제",
)
def delete_program_apply_route(
    pa_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_program_apply = crud.get_program_apply(db, pa_id)
    if not db_program_apply:  # None 체크 추가
        raise HTTPException(status_code=404, detail="Program apply not found")
    if db_program_apply.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own program applies."
        )
    if crud.delete_program_apply(db, pa_id):
        return {"detail": "Program apply successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="Unable to delete program apply")


# 강사가 등록한 프로그램에 신청한 의뢰자 목록 조회
@router.get(
    "/{program_id}/applies",
    response_model=List[schemas.ProgramApply],
    summary="프로그램별 신청 현황",
    description="프로그램별 신청 현황",
)
def get_program_applies(
    program_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    program = crud.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    if program.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can only view applies for your own programs"
        )
    return crud.get_program_applies_by_program_id(db, program_id)
