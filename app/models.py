# 데이터베이스 모델을 SQLAlchemy ORM을 사용하여 정의
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Time,
    Date,
    Enum,
)
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from passlib.context import CryptContext
import pytz

# passlib을 사용하여 비밀번호 해싱을 위한 컨텍스트 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 사용자 정보 테이블
class User(Base):
    __tablename__ = "users"  # 데이터베이스에서 사용할 테이블 이름

    # 데이터베이스 열(Column) 정의:
    user_id = Column(String(20), primary_key=True)  # 사용자 ID, 기본키
    user_password = Column(
        String(70), nullable=False
    )  # 사용자 비밀번호, null 허용하지 않음

    user_name = Column(
        String(18), nullable=False
    )  # 사용자 이름, 최대 길이 18, null 허용하지 않음
    user_phoneNumber = Column(
        String(11), nullable=False, unique=True
    )  # 휴대전화번호(유일)
    user_email = Column(String, nullable=False, unique=True)  # 사용자 이메일(유일)
    user_type = Column(
        Enum("강사", "강의 의뢰자", name="user_type_enum"), nullable=False
    )  # 사용자 유형: 강사, 강의 의뢰자
    user_registrationDate = Column(DateTime)  # 가입일자
    user_update = Column(
        DateTime, nullable=True
    )  # 회원정보 수정 일자 및 시간, null 허용
    user_isDisabled = Column(
        Boolean, default=False
    )  # 계정 비활성화 여부, 기본값은 False

    # 관계 설정
    program_applies = relationship("ProgramApply", back_populates="user")
    request_applies = relationship("RequestApply", back_populates="user")

    # 비밀번호 검증 메소드
    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.user_password)

    # 비밀번호 해싱(정적 메소드)
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    # UTC 시간을 KST로 변환
    @staticmethod
    def get_kst_now():
        utc_now = datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)  # 현재 시각을 UTC로 설정
        kst_now = utc_now.astimezone(pytz.timezone("Asia/Seoul"))  # KST 시간대로 변환
        return kst_now


# 프로그램 정보 테이블
class Program(Base):
    __tablename__ = "programs"
    program_id = Column(Integer, primary_key=True, index=True)  # 프로그램 ID
    program_name = Column(String(30), nullable=False)  # 프로그램명
    program_description = Column(String(300), nullable=False)  # 프로그램 내용
    program_time = Column(Integer)  # 프로그램 진행 시간(ex 1시간 진행)
    program_targetOrganization = Column(
        String(20), nullable=False
    )  # 프로그램 대상(누굴 가르칠 수 있는지)
    program_onOffline = Column(String)  # 온/오프라인
    program_maxCapacity = Column(
        Integer, nullable=True
    )  # 최대 수용 가능 인원(선택항목, Null 허용)
    program_portfolioUrl = Column(
        String, nullable=True
    )  # 포트폴리오 url(선택항목, Null 허용)
    user_id = Column(
        String(20), ForeignKey("users.user_id")
    )  # 프로그램을 등록한 사용자 ID
    program_interruption = Column(
        Boolean, default=False
    )  # 프로그램 중단, 기본값은 False

    # 관계 설정
    applies = relationship("ProgramApply", back_populates="program")


# 강의 의뢰 정보 테이블
class Request(Base):
    __tablename__ = "requests"
    request_id = Column(Integer, primary_key=True, index=True)  # 강의 의뢰 ID
    request_subject = Column(String(30))  # 강의 의뢰 제목
    request_content = Column(String(300))  # 강의 의뢰 내용
    request_targetAudience = Column(String(20))  # 강의 대상
    request_date = Column(Date)  # 강의 날짜
    request_startTime = Column(String)  # 강의 시작 시간
    request_endTime = Column(String)  # 강의 종료 시간
    request_qualifications = Column(String(100), nullable=True)  # 필요 자격, null 허용
    request_onOffline = Column(String)  # 온/오프라인
    request_place = Column(
        String(50), nullable=True
    )  # 강의 장소 (오프라인일 경우 활성화))
    request_detailedAddress = Column(
        String(200), nullable=True
    )  # 온라인: 비활성화, 오프라인일 경우 상세주소(시군구 뒤에 입력하는 거), null허용
    request_audienceCount = Column(Integer)  # 강의 대상 인원
    request_lectureFee = Column(Integer)  # 강의료
    user_id = Column(String(20), ForeignKey("users.user_id"))  # 의뢰를 등록한 사용자 ID
    request_completed = Column(Boolean, default=False)  # 강의의뢰 완료, 기본값은 False

    # 관계 설정
    applies = relationship("RequestApply", back_populates="request")


# 프로그램 신청 내역 테이블
class ProgramApply(Base):
    __tablename__ = "program_apply"
    pa_id = Column(Integer, primary_key=True, index=True)  # 신청 ID(자동)
    program_id = Column(
        Integer, ForeignKey("programs.program_id"), nullable=False
    )  # 프로그램 ID(프론트)
    user_id = Column(
        String, ForeignKey("users.user_id"), nullable=False
    )  # 사용자 ID(프론트)
    pa_lectureFee = Column(Integer, nullable=False)  # 급여
    pa_date = Column(Date, nullable=False)  # 강의 날짜
    pa_startTime = Column(Time, nullable=True)  # 시작 시간
    pa_endTime = Column(Time, nullable=True)  # 종료 시간
    pa_onOffline = Column(String, nullable=True)  # 온/오프라인 여부
    pa_address = Column(String, nullable=True)  # 주소
    pa_detailedAddress = Column(String, nullable=True)  # 상세 주소
    pa_targetAudience = Column(String, nullable=True)  # 강의 대상
    pa_personnel = Column(Integer, nullable=False)  # 강의 인원
    pa_status = Column(
        Enum("수락", "거절", "대기", name="pa_status_enum"),
        nullable=False,
        default="대기",
    )  # 신청 상태(백엔드)
    program_name = Column(String, nullable=False)  # 프로그램명 (트리거로 채움)
    user_name = Column(String, nullable=False)  # 사용자 이름 (트리거로 채움)
    user_phoneNumber = Column(String, nullable=False)  # 휴대전화번호 (트리거로 채움)

    # 관계 설정
    program = relationship("Program", back_populates="applies")
    user = relationship("User", back_populates="program_applies")


# 강의 의뢰 지원 내역 테이블
class RequestApply(Base):
    __tablename__ = "request_apply"
    ra_id = Column(Integer, primary_key=True, index=True)  # 지원 ID(자동)
    request_id = Column(
        Integer, ForeignKey("requests.request_id"), nullable=False
    )  # 강의 의뢰 ID
    user_id = Column(
        String, ForeignKey("users.user_id"), nullable=False
    )  # 사용자 ID(프론트)
    # ra_startTime = Column(Time, nullable=True)  # 시작 시간 추가
    # ra_endTime = Column(Time, nullable=True)  # 종료 시간 추가
    ra_status = Column(
        Enum("수락", "거절", "대기", name="ra_status_enum"),
        nullable=False,
        default="대기",
    )  # 지원 상태
    request_subject = Column(String, nullable=False)  # 강의 의뢰 제목 (트리거로 채움)
    user_name = Column(String, nullable=False)  # 사용자 이름 (트리거로 채움)
    user_email = Column(String, nullable=False)  # 사용자 이메일
    user_phoneNumber = Column(String, nullable=False)  # 사용자 전화번호
    ra_dateOfBirth = Column(Date, nullable=False)  # 생년월일
    ra_gender = Column(
        Enum("남성", "여성", name="ra_gender_enum"), nullable=False
    )  # 성별

    # 관계 설정
    request = relationship("Request", back_populates="applies")
    user = relationship("User", back_populates="request_applies")
