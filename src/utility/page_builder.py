import datetime
import logging as log

from sqlmodel import Session, select

from src.models.chat import Chat
from src.models.holiday import Holiday, HolidayType
from src.constants import engine, tzinfo, Date
from src.utility.site_parser import parse_site


async def build_pages(chat_id: int, date: Date | None = None):
    CHUNK_SIZE = 13
    CHUNK_OVERHEAD = 6
    
    if not date:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = Date(day=tnow.day, month=tnow.month)
    
    holidays: dict = {
        'normal': [],
        'country_specific' : ['------- Национальные праздники -------'],
        'church' : ['------- Церковные праздники -------'],
    }
    
    with Session(engine) as session:
        selected = select(Holiday).where(Holiday.day == date.day).where(Holiday.month == date.month)
        results = session.exec(selected)
        
        if not results.all(): # If site is not parsed somehow
            log.info('Parsing site from page_builder.')
            await parse_site(date=date)
            
        results = session.exec(selected)
            
        chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
        
        for element in results:
            holiday_text = f'● {element.name}'
            
            if element.type == HolidayType.normal:
                holidays['normal'].append(holiday_text)
            elif element.type == HolidayType.church and chat.send_church_holidays:
                holidays['church'].append(holiday_text)
            elif element.type == HolidayType.country_specific and chat.send_country_specific:
                holidays['country_specific'].append(holiday_text)
                
    for key in holidays.keys():
        if key == 'normal':
            continue
        if len(holidays[key]) == 1:
            holidays[key] = []
    
    holiday_count = 0
    
    for key in holidays.keys():
        if key != 'normal':
            holiday_count -= 1
        holiday_count += len(holidays[key])
            
    chunk_count = holiday_count // CHUNK_SIZE
    if (holiday_count % CHUNK_SIZE) > CHUNK_OVERHEAD:
        chunk_count += 1
    
    holiday_page_count = 0
    pages = ['']
    
    for key in holidays.keys():
        if len(holidays[key]) == 0:
            continue
        for holiday in holidays[key]:
            if holiday == holidays[key][0] and key != 'normal' and holiday_page_count < CHUNK_SIZE:
                pages[len(pages)-1] += f'{holiday}\n'
            elif holiday_page_count < CHUNK_SIZE or (chunk_count == len(pages) and holiday_page_count >= CHUNK_SIZE):
                pages[len(pages)-1] += f'{holiday}\n'
                holiday_page_count += 1
            else:
                holiday_page_count = 1
                pages.append(f'{holiday}\n')
    
    return pages