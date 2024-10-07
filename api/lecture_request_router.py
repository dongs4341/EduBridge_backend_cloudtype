from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.crud as crud
import app.schemas as schemas
import app.auth as auth
from app.database import SessionLocal
from typing import List
from app.utils import format_date, shorten_text  # 유틸리티 함수 가져오기

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 강의의뢰 등록
@router.post(
    "/",
    response_model=schemas.LectureRequestSchema,
    status_code=status.HTTP_201_CREATED,
    summary="강의의뢰 등록",
)
def create_lecture_request_route(
    request: schemas.LectureRequestCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.user_type != "강의 의뢰자":
        raise HTTPException(
            status_code=403, detail="Only requesters can create lecture requests."
        )
    return crud.create_lecture_request(db, request, current_user.user_id)


# 강의의뢰 수정
@router.put(
    "/{request_id}",
    response_model=schemas.LectureRequestSchema,
    summary="강의의뢰 수정",
)
def update_lecture_request_route(
    request_id: int,
    request: schemas.LectureRequestUpdate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_request = crud.get_lecture_request_by_id(db, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Lecture request not found")
    if db_request.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the request creator can modify this lecture request.",
        )
    return crud.update_lecture_request(db, request_id, request)


# 강의의뢰 삭제
@router.delete("/{request_id}", response_model=dict, summary="강의의뢰 삭제")
def delete_lecture_request_route(
    request_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_request = crud.get_lecture_request_by_id(db, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Lecture request not found")
    if db_request.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the request creator can delete this lecture request.",
        )
    try:
        if not crud.delete_lecture_request(db, request_id):
            raise HTTPException(
                status_code=404, detail="Unable to delete lecture request"
            )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return {"detail": "Lecture request successfully deleted"}


# 강의의뢰 검색
@router.post(
    "/search",
    response_model=List[schemas.LectureRequestListSchema],
    summary="강의의뢰 검색",
)
def search_lecture_requests(search_query: str, db: Session = Depends(get_db)):
    lecture_requests = crud.search_lecture_requests(db, search_query=search_query)
    if not lecture_requests:
        raise HTTPException(status_code=404, detail="lecture requests not found")
    summarized_requests = []
    for request in lecture_requests:
        formatted_date = format_date(request.request_date)
        summarized_request = {
            "request_subject": request.request_subject,
            "request_content": shorten_text(request.request_content, 50),
            "request_targetAudience": shorten_text(request.request_targetAudience, 10),
            "request_place": request.request_place,
            "request_date": formatted_date,
            "request_startTime": request.request_startTime,
            "request_endTime": request.request_endTime,
            "request_onOffline": request.request_onOffline,
            "request_completed": request.request_completed,
            "request_id": request.request_id,
            "user_id": request.user_id,
        }
        summarized_requests.append(summarized_request)
    return summarized_requests


# 모든 강의의뢰 조회
@router.get(
    "/list",
    response_model=List[schemas.LectureRequestListSchema],
    summary="모든 강의의뢰 조회",
)
def get_lecture_requests_summary(db: Session = Depends(get_db)):
    lecture_requests = crud.get_all_lecture_requests(db)
    if not lecture_requests:
        raise HTTPException(status_code=404, detail="No lecture requests found.")
    summarized_requests = []
    for request in lecture_requests:
        formatted_date = format_date(request.request_date)
        summarized_request = {
            "request_subject": request.request_subject,
            "request_content": shorten_text(request.request_content, 50),
            "request_targetAudience": shorten_text(request.request_targetAudience, 10),
            "request_place": request.request_place,
            "request_date": formatted_date,
            "request_startTime": request.request_startTime,
            "request_endTime": request.request_endTime,
            "request_onOffline": request.request_onOffline,
            "request_completed": request.request_completed,
            "request_id": request.request_id,
            "user_id": request.user_id,
            "request_lectureFee": request.request_lectureFee,
            "request_detailedAddress": request.request_detailedAddress,
            "request_qualifications": request.request_qualifications,
            "request_audienceCount": request.request_audienceCount,
        }
        summarized_requests.append(summarized_request)
    return summarized_requests


# 강의의뢰 상세 조회
@router.get(
    "/{request_id}",
    # response_model=schemas.LectureRequestDetail,
    summary="강의의뢰 상세 조회",
)
def get_lecture_request_detail_route(
    request_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    request_detail = crud.get_lecture_request_detail(
        db, request_id, current_user.user_id
    )
    if not request_detail:
        raise HTTPException(status_code=404, detail="Lecture request not found")

    return request_detail


# 강의의뢰 지원 수락
@router.post(
    "/request-applies/{ra_id}/accept",
    response_model=schemas.RequestApply,
    summary="강의의뢰 지원 수락",
    description="강의의뢰에 지원한 강사를 수락",
)
def accept_request_apply_route(
    ra_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_request_apply = crud.get_request_apply(db, ra_id)
    if not db_request_apply:  # None 체크 추가
        raise HTTPException(status_code=404, detail="Request apply not found")

    if db_request_apply.request.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only accept request applies for your own requests.",
        )

    return crud.accept_request_apply(db, ra_id)


# 강의의뢰 지원 거절
@router.post(
    "/request-applies/{ra_id}/reject",
    response_model=schemas.RequestApply,
    summary="강의의뢰 지원 거절",
    description="강의의뢰에 지원한 강사를 거절",
)
def reject_request_apply_route(
    ra_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_request_apply = crud.get_request_apply(db, ra_id)
    if not db_request_apply:  # None 체크 추가
        raise HTTPException(status_code=404, detail="Request apply not found")

    if db_request_apply.request.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only reject request applies for your own lecture requests.",
        )

    return crud.reject_request_apply(db, ra_id)


# 강의의뢰 지원
@router.post(
    "/request-applies",
    response_model=schemas.RequestApply,
    status_code=status.HTTP_201_CREATED,
    summary="강의의뢰 지원",
)
def create_request_apply_route(
    request_apply: schemas.RequestApplyCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return crud.create_request_apply(
        db=db, request_apply=request_apply, user_id=current_user.user_id
    )


# 강의의뢰에 지원한 특정 의뢰 내역 조회
@router.get(
    "/request-applies/{ra_id}",
    response_model=schemas.RequestApply,
    summary="강의의뢰별 지원 현황",
    description="강의의뢰에 지원한 특정 의뢰 내역 조회",
)
def read_request_apply_route(ra_id: int, db: Session = Depends(get_db)):
    db_request_apply = crud.get_request_apply(db=db, ra_id=ra_id)
    if not db_request_apply:
        raise HTTPException(status_code=404, detail="Request apply not found")
    return db_request_apply


# 강의의뢰 지원 내용 수정
@router.put(
    "/request-applies/{ra_id}",
    response_model=schemas.RequestApply,
    summary="특정 강의의뢰 지원 내용 수정",
    description="강의의뢰 지원 시 작성하였던 내용 수정.",
)
def update_request_apply_route(
    ra_id: int,
    request_apply: schemas.RequestApplyCreate,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_request_apply = crud.get_request_apply(db, ra_id)
    if not db_request_apply:
        raise HTTPException(status_code=404, detail="Request apply not found")

    if db_request_apply.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can only modify your own request applies."
        )
    return crud.update_request_apply(db, ra_id, request_apply)


# 강의의뢰 지원 취소
@router.delete(
    "/request-applies/{ra_id}",
    response_model=dict,
    summary="특정 강의의뢰 지원 취소",
    description="강의의뢰 지원 시 작성하였던 내역 취소.",
)
def delete_request_apply_route(
    ra_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_request_apply = crud.get_request_apply(db, ra_id)
    if not db_request_apply:  # None 체크 추가
        raise HTTPException(status_code=404, detail="Request apply not found")

    if db_request_apply.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own request applies."
        )
    if crud.delete_request_apply(db, ra_id):
        return {"detail": "Request apply successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="Unable to delete request apply")


# 의뢰자가 등록한 강의의뢰에 지원한 강사 목록 조회
@router.get(
    "/{request_id}/applies",
    response_model=List[schemas.RequestApply],
    summary="강의의뢰별 지원 현황",
    description="강의의뢰별 지원 현황",
)
def get_request_applies(
    request_id: int,
    current_user=Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    request = crud.get_lecture_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Lecture request not found")
    if request.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only view applies for your own lecture requests",
        )
    return crud.get_request_applies_by_request_id(db, request_id)
