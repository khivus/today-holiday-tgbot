import datetime

from sqlmodel import Session, select

from src.models.holiday import Holiday
from src.constants import engine, tzinfo, Date


def get_holiday_message(page_index: int, pages: list[str], date: Date | None = None) -> str:
    
    tnow = datetime.datetime.now(tz=tzinfo)
    if not date:
        date = Date(day=tnow.day, month=tnow.month)
        weekday = tnow.weekday()
    else:
        weekday = datetime.datetime(year=tnow.year, month=date.month, day=date.day).weekday()

    weekdays: dict = {
        0 : 'понедельник',
        1 : 'вторник',
        2 : 'среду',
        3 : 'четверг',
        4 : 'пятницу',
        5 : 'субботу',
        6 : 'воскресенье'
    }

    max_index = len(pages)
    endl: str = '\n'
    msg_start = f'Праздники на {weekdays[weekday]} {date.day:02}.{date.month:02}:\n{endl:->50}'
    msg_end = f'{endl:->50}Страница {page_index + 1}/{max_index}'
    page = pages[page_index]
    message = msg_start + page + msg_end
    return message


async def build_pages(date: Date | None = None) -> list[str]:
    CHUNK_SIZE = 13
    CHUNK_OVERHEAD = 6
    
    if not date:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = Date(day=tnow.day, month=tnow.month)
    
    holidays: list = []
    
    with Session(engine) as session:
        results = session.exec(select(Holiday).where(Holiday.day == date.day).where(Holiday.month == date.month))
        
        for element in results:
            holiday_text = f'● {element.name}'
            holidays.append(holiday_text)
    
    holiday_count = len(holidays)
    
    chunk_count = holiday_count // CHUNK_SIZE
    if (holiday_count % CHUNK_SIZE) > CHUNK_OVERHEAD:
        chunk_count += 1
    
    holiday_page_count = 0
    pages = ['']
    
    for holiday in holidays:
        if holiday_page_count < CHUNK_SIZE or (chunk_count == len(pages) and holiday_page_count >= CHUNK_SIZE):
            pages[len(pages)-1] += f'{holiday}\n'
            holiday_page_count += 1
        else:
            holiday_page_count = 1
            pages.append(f'{holiday}\n')
    
    return pages