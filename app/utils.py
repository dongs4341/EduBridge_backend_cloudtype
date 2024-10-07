from datetime import date

# 날짜와 시간을 포맷팅하는 함수
def format_date(start_date: date) -> str:
    # 요일을 한국어로 정의
    korean_weekdays = ["월", "화", "수", "목", "금", "토", "일"]

    weekday = korean_weekdays[start_date.weekday()]  # 요일을 영어로 가져오기
    date_str = start_date.strftime('%y/%m/%d')  # 년/월/일
    return f"{date_str} ({weekday})"
'''
def format_date_time(start_date: date, start_time: str, end_time: str) -> str:
    formatted_date = format_date(start_date)
    return f"{formatted_date} {start_time} - {end_time}"
'''
# 내용 및 대상 글자 제한 함수
def shorten_text(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + '...'
