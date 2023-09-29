import datetime

from sqlmodel import Session, select

from src.models.chat import Chat
from src.models.holiday import Holiday, HolidayType
from src.constants import engine


def build_pages(chat_id: int):
    CHUNK_SIZE = 15
    CHUNK_OVERHEAD = 5
    today = datetime.date.today()
    day = today.day
    month = today.month
    holidays: dict = {
        'normal': [],
        'country_specific' : ['------- Национальные праздники -------'],
        'church' : ['------- Церковные праздники -------'],
        'name_day' : ['------- Именины -------']
    }
    
    with Session(engine) as session:
        results = session.exec(select(Holiday).where(
            Holiday.day == day).where(Holiday.month == month))
        chat = session.exec(select(Chat).where(
            Chat.id == chat_id)).one()

        for element in results:
            holiday_text = f'- {element.name}'
            if element.years_passed is not None:
                holiday_text += f' - {element.years_passed}'
            
            if element.type == HolidayType.normal:
                holidays['normal'].append(holiday_text)
            elif element.type == HolidayType.church and chat.send_church_holidays:
                holidays['church'].append(holiday_text)
            elif element.type == HolidayType.country_specific and chat.send_country_specific:
                holidays['country_specific'].append(holiday_text)
            elif element.type == HolidayType.name_day and chat.send_name_days:
                holidays['name_day'].append(holiday_text)
                
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
    if holiday_count % CHUNK_SIZE > CHUNK_OVERHEAD:
        chunk_count += 1
    
    holiday_page_count = 0
    pages = ['']
    
    for key in holidays.keys():
        if len(holidays[key]) == 0:
            continue
        for holiday in holidays[key]:
            if holiday == holidays[key][0] and key != 'normal':
                pages[len(pages)-1] += f'{holiday}\n'
            elif holiday_page_count < CHUNK_SIZE or chunk_count == len(pages):
                pages[len(pages)-1] += f'{holiday}\n'
                holiday_page_count += 1
            else:
                holiday_page_count = 1
                pages.append(f'{holiday}\n')
    
    return pages