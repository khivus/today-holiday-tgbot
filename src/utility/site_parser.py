import aiohttp
import datetime
import re
import json
import logging as log

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from user_agent import generate_user_agent

from src.models.holiday import HolidayType, Holiday
from src.constants import engine, tzinfo, Date

async def parse_site(
    url: str | None = None, 
    date: Date | None = None
    ) -> None:
    
    if not date:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = Date(day=tnow.day, month=tnow.month)
    
    if not url:
        url = f'https://calend.online/holiday/day/{date.day}-{date.month}/'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
            body = await response.text(encoding='utf-8')
    
    soup = BeautifulSoup(body, 'html.parser')
    site_list = soup.find('ul', class_='holidays-list')

    if not site_list:
        log.error(f'Site don\'t parsed!')
        return False
    
    with open('filter_words.json', 'r') as file:
        filter_words = json.load(file)

    church_words = '|'.join(filter_words['church'])
    church_pattern = re.compile(rf'.*({church_words}).*',re.IGNORECASE)
    country_words = '|'.join(filter_words['international'])
    country_specific_pattern = re.compile(rf'.*({country_words}).*',re.IGNORECASE)
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
            Holiday.day == date.day).where(Holiday.month == date.month))
        
        for saved_holiday in results:
            session.delete(saved_holiday)
            
        for pending_holiday in holidays_list:
            holiday = Holiday(name=pending_holiday[0], type=pending_holiday[1], day=date.day, month=date.month)
            session.add(holiday)
            
        session.commit()
    
    return True
