# Pydantic을 사용하여 요청과 응답 스키마 정의
from pydantic import BaseModel, EmailStr, Field, constr, HttpUrl, validator
from enum import Enum
from typing import Optional
from datetime import datetime, date, time
from app.utils import format_date


# user_type을 위한 Enum 정의
class UserTypeEnum(str, Enum):
    instructor = "강사"
    requester = "강의 의뢰자"


# 사용자 생성을 위한 필드 정의
class UserCreate(BaseModel):
    user_id: constr(min_length=6, max_length=20)  # 최소 6자, 최대 20자
    user_name: constr(max_length=18)
    user_password: constr(min_length=6, max_length=20)
    user_phoneNumber: constr(pattern=r"^\d{11}$")  # 숫자만 11자리
    user_email: EmailStr  # 유효한 이메일 형식인지 검증
    user_type: UserTypeEnum  # Enum 사용하여 값 제한 // 사용자 유형 (예: 강사)


# 사용자 정보 업데이트를 위한 선택적 필드
class UserUpdate(BaseModel):
    user_name: Optional[constr(max_length=18)] = None
    user_password: Optional[str] = None
    user_phoneNumber: Optional[constr(pattern=r"^\d{11}$")] = None
    user_email: Optional[EmailStr] = None


class UserInDB(UserCreate):
    user_password: str  # DB에 저장된 해시된 비밀번호
    user_registrationDate: datetime = datetime.utcnow()  # 사용자 등록 날짜
    user_isDisabled: bool = False  # 계정 비활성화 여부

    class Config:
        from_attributes = True


# UserCreate의 확장으로 추가 데이터 없이 모든 속성 상속
class User(UserInDB):
    pass


# 사용자 ID 찾기 요청을 위한 이름과 이메일 필드
class UserIdFind(BaseModel):
    user_name: constr(max_length=18)
    user_email: EmailStr


# 비밀번호 찾기 요청을 위한 ID와 이메일 필드
class UserPasswordFind(BaseModel):
    user_id: constr(min_length=6, max_length=20)
    user_email: EmailStr


# 프로그램 등록
class ProgramCreate(BaseModel):
    program_name: constr(max_length=30)
    program_description: constr(max_length=300)
    program_time: int  # 1시간 단위로 진행 시간 입력
    program_targetOrganization: constr(max_length=20)
    program_onOffline: str  # "온라인", "오프라인" 또는 둘 다
    program_maxCapacity: Optional[int] = None  # 선택적 필드, 0보다 큰 수만 허용
    program_portfolioUrl: Optional[HttpUrl] = None  # URL 형식


# 프로그램 수정
class ProgramUpdate(BaseModel):
    program_name: Optional[str] = None
    program_description: Optional[str] = None
    program_time: Optional[int] = None
    program_targetOrganization: Optional[str] = None
    program_onOffline: Optional[str] = None  # "온라인", "오프라인" 또는 둘 다
    program_maxCapacity: Optional[int] = None
    program_portfolioUrl: Optional[HttpUrl] = None  # URL 형식


class Program(ProgramCreate):
    program_id: int
    user_id: constr(min_length=6, max_length=20)

    class Config:
        from_attributes = True


# 프로그램 검색 목록 생성을 위한 필드 정의
class ProgramSchema(BaseModel):
    program_name: str
    program_description: str
    program_targetOrganization: str
    program_onOffline: str
    program_interruption: bool = False
    program_id: int
    user_id: str
    program_time: int
    program_maxCapacity: int
    program_portfolioUrl: str


# 프로그램 상세 정보 생성을 위한 필드 정의
class ProgramDetail(ProgramSchema):
    program_id: int
    program_name: str
    program_description: str
    program_targetOrganization: str
    program_onOffline: str
    program_interruption: bool
    user_id: str
    is_applied: bool
    is_owner: bool
    program_time: int
    program_maxCapacity: int
    program_portfolioUrl: str

    class Config:
        from_attributes = True


# 강의 의뢰 등록
class LectureRequestCreate(BaseModel):
    request_subject: str = Field(..., max_length=30)  # 강의 의뢰 제목, 제목 30글자 이내
    request_content: str = Field(
        ..., max_length=300
    )  # 강의 의뢰 내용, 내용 300글자 이내
    request_targetAudience: str = Field(..., max_length=20)  # 강의 대상 20글자 이내
    request_date: date  # 강의 날짜
    request_startTime: str  # 강의 시작 시간
    request_endTime: str  # 강의 종료 시간
    request_qualifications: Optional[str] = Field(
        None, max_length=100
    )  # 선택 항목, 100글자 이내
    request_onOffline: str  # 온/오프라인
    request_place: Optional[str] = None  # 강의 장소
    request_detailedAddress: Optional[str] = (
        None  # 온라인: 비활성화, 오프라인: 상세 주소(시군구 뒤에 입력하는 거)
    )
    request_audienceCount: Optional[int] = Field(None, ge=1)  # 숫자 입력
    request_lectureFee: Optional[int] = Field(ge=1)  # 만 원 단위로 입력


# 강의 의뢰 수정
class LectureRequestUpdate(BaseModel):
    request_subject: Optional[str] = Field(None, max_length=30)
    request_content: Optional[str] = Field(None, max_length=300)
    request_targetAudience: Optional[str] = Field(None, max_length=20)
    request_date: Optional[date] = None
    request_startTime: Optional[str] = None
    request_endTime: Optional[str] = None
    request_qualifications: Optional[str] = Field(None, max_length=100)
    request_onOffline: Optional[str] = None
    request_place: Optional[str] = None
    request_detailedAddress: Optional[str] = None
    request_audienceCount: Optional[int] = Field(None, ge=1)
    request_lectureFee: Optional[int] = Field(ge=1)


# 강의 의뢰 데이터 응답
class LectureRequestSchema(LectureRequestCreate):
    request_completed: bool = False
    request_id: int
    user_id: str

    class Config:
        from_attributes = True


# 강의 의뢰 목록 생성을 위한 필드 정의
class LectureRequestListSchema(BaseModel):
    request_subject: str
    request_content: str
    request_targetAudience: str
    request_place: Optional[str] = None
    request_date: str  # 강의 날짜
    request_startTime: str  # 강의 시작 시간
    request_endTime: str  # 강의 종료 시간
    request_onOffline: str
    request_completed: bool = False
    request_id: int
    user_id: str
    request_lectureFee: int
    request_detailedAddress: Optional[str] = None
    request_qualifications: str
    request_audienceCount: int

    @validator("request_date", pre=True, allow_reuse=True)
    def date_string(cls, value):
        if isinstance(value, date):
            return format_date(value)
        return value


# 강의 의뢰 상세 정보 생성을 위한 필드 정의
class LectureRequestDetail(LectureRequestListSchema):
    request_audienceCount: int
    request_lectureFee: int
    request_qualifications: Optional[str] = None
    request_detailedAddress: Optional[str] = None

    is_applied: bool  # 추가 필드
    is_owner: bool  # 추가 필드

    class Config:
        from_attributes = True


# 프로그램 신청 내역 스키마
class ProgramApplyBase(BaseModel):
    program_id: int
    pa_lectureFee: int
    pa_date: date
    pa_startTime: Optional[time] = None
    pa_endTime: Optional[time] = None
    pa_onOffline: Optional[str] = None
    pa_address: Optional[str] = None
    pa_detailedAddress: Optional[str] = None
    pa_targetAudience: Optional[str] = None
    pa_personnel: int


class ProgramApplyCreate(ProgramApplyBase):
    pass


class ProgramApply(ProgramApplyBase):
    pa_id: int
    program_name: str
    user_name: str
    user_phoneNumber: str
    matching_status: Optional[str] = None

    class Config:
        from_attributes = True


# 강의 의뢰 지원 내역 스키마
class RequestApplyBase(BaseModel):
    request_id: int
    ra_dateOfBirth: date
    ra_gender: str = Field(..., example="남성")


class RequestApplyCreate(BaseModel):
    request_id: int
    ra_dateOfBirth: date
    ra_gender: str = Field(..., example="남성")


class RequestApply(RequestApplyBase):
    ra_id: int
    request_subject: str
    user_name: str
    user_email: str
    user_phoneNumber: str
    matching_status: Optional[str] = None

    class Config:
        from_attributes = True


# 강사의 강의 의뢰 지원 응답 스키마
class RequestApplyWithStatus(BaseModel):
    request_id: int
    ra_id: int
    request_subject: str
    request_content: str
    request_targetAudience: str
    request_date: date
    request_startTime: str
    request_endTime: str
    request_qualifications: Optional[str]
    request_onOffline: str
    request_place: Optional[str]
    request_detailedAddress: Optional[str]
    request_audienceCount: int
    request_lectureFee: int
    matching_status: str

    class Config:
        from_attributes = True


# 강의 의뢰자의 프로그램 신청 응답 스키마
class ProgramApplyWithStatus(BaseModel):
    program_id: int
    pa_id: int
    program_name: str
    program_description: str
    program_time: int
    program_targetOrganization: str
    program_onOffline: str
    program_maxCapacity: Optional[int]
    program_portfolioUrl: Optional[str]
    matching_status: str

    class Config:
        from_attributes = True
