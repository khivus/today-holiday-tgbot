import datetime

from sqlmodel import Session, select

from src.models.holiday import Holiday
from src.constants import engine, tzinfo, Date


async def build_pages(date: Date | None = None):
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