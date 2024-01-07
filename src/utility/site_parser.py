import aiohttp
import datetime
import re
import logging as log

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from user_agent import generate_user_agent

from src.models.holiday import HolidayType, Holiday
from src.constants import engine, tzinfo

async def parse_site(
    url: str | None = None, 
    date: list[int] | None = None
    ) -> None:
    
    if not date:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = [tnow.day, tnow.month]
    
    if not url:
        url = f'https://calend.online/holiday/day/{date[0]}-{date[1]}/'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
            body = await response.text(encoding='utf-8')
    
    soup = BeautifulSoup(body, 'html.parser')
    site_list = soup.find('ul', class_='holidays-list')

    # for word in church_banwords:
    #     church_words = word.con('|')
    # church_pattern = re.compile(rf'.*({church_words}).*',re.IGNORECASE)
    
    church_pattern = re.compile(
        r'.*(День памяти|Собор|Католический|Буддийский|Зороастрийский|иконы Божией Матери|Пресвятой|Богородицы|Митры|Именины|Мученик).*',
        re.IGNORECASE)
    country_specific_pattern = r'.*( - ).*'
    holidays_list: list = []

    for element in site_list:
        holiday_name = element.text.strip()
        
        if holiday_name == '':
            continue
        
        if re.match(country_specific_pattern, holiday_name):
            holiday_type = HolidayType.country_specific
        elif re.match(church_pattern, holiday_name):
            holiday_type = HolidayType.church
        else:
            holiday_type = HolidayType.normal
        
        holidays_list.append([holiday_name, holiday_type])

    if len(holidays_list) == 0:
        log.error(f'Site don\'t parsed!')
        return False
        
    with Session(engine) as session:
        results = session.exec(select(Holiday).where(
            Holiday.day == date[0]).where(Holiday.month == date[1]))
        
        for saved_holiday in results:
            session.delete(saved_holiday)
            
        for pending_holiday in holidays_list:
            holiday = Holiday(name=pending_holiday[0], type=pending_holiday[1], day=date[0], month=date[1])
            session.add(holiday)
            
        session.commit()
    
    return True
