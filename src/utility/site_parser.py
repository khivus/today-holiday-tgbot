import aiohttp
import datetime
import re
import logging as log

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from user_agent import generate_user_agent

from src.models.holiday import HolidayType, Holiday
from src.constants import engine


async def parse_site(url: str = 'https://kakoysegodnyaprazdnik.ru/', *, additional_info: str = '', add_to_db: bool = True, date: list[int] = None) -> None:

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
            body = await response.text(encoding='utf-8')

    soup = BeautifulSoup(body, 'html.parser')
    listl = soup.find('div', class_='listing_wr')

    elements: list[str] = []
    i = 0
    name_day_counter = 0

    for element in listl:
        if (element.name == 'div'):
            attributes = element.attrs

            dicts_separator = [{'class': ['hr-hr_leto']}, {'class': ['hr-hr_vesna']},
                               {'class': ['hr-hr_winter']}, {'class': ['hr-hr_osen']}, {'id': 'prin'}]
            dicts_holidays = [{'itemprop': 'acceptedAnswer', 'itemscope': '', 'itemtype': 'http://schema.org/Answer'},
                              {'itemprop': 'suggestedAnswer', 'itemscope': '', 'itemtype': 'http://schema.org/Answer'}]

            if attributes in dicts_separator:
                i += 1

            elif attributes in dicts_holidays:
                holiday_name = element.find('span', itemprop='text').text

                years = element.find('span', class_='super')
                if years is not None:
                    years_passed = str(years.text)
                else:
                    years_passed = None

                match i:
                    case 0: 
                        holiday_type = HolidayType.normal
                    case 1: 
                        holiday_type = HolidayType.church
                    case 2: 
                        holiday_type = HolidayType.country_specific
                    case 3: 
                        holiday_type = HolidayType.name_day
                        name_day_counter += 1

                elements.append([holiday_name, holiday_type, years_passed])
    
    if len(elements) == 0:
        log.error(f'{additional_info}Site don\'t parsed!')
        return False
    
    church_pattern1 = r'^(День памяти|Собор|Католический|Буддийский|Зороастрийский|Праздник иконы Божией Матери).*'
    church_pattern2 = r'(иконы Божией Матери)$'
    country_specific_pattern = r'.*( - ).*'
    name_day_pattern = r'^Именины.*'
    bad_site = False
    
    if name_day_counter == 0:
        for holiday in elements:
            if re.match(name_day_pattern, holiday[0]) and holiday[1] == HolidayType.country_specific:
                bad_site = True
                break
            
        if bad_site:
            for holiday in elements:
                holiday_type = holiday[1]
                
                if re.match(church_pattern1, holiday[0]) or re.match(church_pattern2, holiday[0]): # church
                    holiday_type = HolidayType.church
                elif holiday_type != HolidayType.normal and re.match(country_specific_pattern, holiday[0]): # country_specific
                    holiday_type = HolidayType.country_specific
                elif re.match(name_day_pattern, holiday[0]) or holiday_type == HolidayType.country_specific: # name_days
                    holiday_type = HolidayType.name_day
                else:
                    holiday_type = HolidayType.normal
                    
                holiday[1] = holiday_type
    else:
        for holiday in elements:
            if (re.match(church_pattern1, holiday[0]) or re.match(church_pattern2, holiday[0])) and holiday[1] == HolidayType.normal:
                holiday[1] = HolidayType.church 

    if add_to_db:
        if not date:
            today = datetime.date.today()
            date = [today.day, today.month]
        
        with Session(engine) as session:
            results = session.exec(select(Holiday).where(
                Holiday.day == date[0]).where(Holiday.month == date[1]))
            
            for saved_holiday in results:
                session.delete(saved_holiday)
                
            for pending_holiday in elements:
                holiday = Holiday(name=pending_holiday[0], type=pending_holiday[1], years_passed=pending_holiday[2], day=date[0], month=date[1])
                session.add(holiday)
                
            session.commit()
    
    return True
