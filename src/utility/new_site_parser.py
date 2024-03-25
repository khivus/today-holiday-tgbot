import aiohttp
import asyncio
import datetime
import logging as log

from sqlmodel import Session, select
from user_agent import generate_user_agent
from bs4 import BeautifulSoup

from src.models.holiday import Holiday
from src.constants import engine, tzinfo, Date


def get_month_name(month: int) -> str:
    months: dict = {
        1 : 'yanvarya',
        2 : 'fevralya',
        3 : 'marta',
        4 : 'aprelya',
        5 : 'maya',
        6 : 'ijunya',
        7 : 'ijulya',
        8 : 'avgusta',
        9 : 'sentyabrya',
        10 : 'oktyabrya',
        11 : 'noyabrya',
        12 : 'dekabrya'
    }
    return months[month]


async def parse_all_site_pages(start_month: int = 1) -> None:
    for chosen_month in range(start_month, 13):
        if chosen_month in [1, 3, 5, 7, 8, 10, 12]:
            days = 31
        elif chosen_month in [4, 6, 9, 11]:
            days = 30
        else:
            days = 29
        for day in range(1, days+1):
            date = Date(day=day, month=chosen_month)
            if await parse_site_page(date=date):
                log.info(f'Done {date.day}.{date.month}')
            else:
                log.error(f'Error parsing {date.day}.{date.month}')
            await asyncio.sleep(3)


def filter_holiday(tags: list) -> bool:
    filterd_tags = tags.copy()
    filter_tags = ['Народные', 'Церковные', 'Православные', 'Католические', 'Национальные',
                    'Лютеранские', 'Конституционные', 'Дни памяти', 'Посты', 'Мусульманские', 'Армейские']
    for tag in tags:
        if tag in filter_tags:
            filterd_tags.remove(tag)
    if filterd_tags == []:
        return True
    else:
        return False


async def parse_site_page(date: Date | None = None) -> bool:
    if not date:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = Date(day=tnow.day, month=tnow.month)
    month = get_month_name(month=date.month)
    url = f'https://kakoyprazdnik.com/den/{date.day}-{month}'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
                body = await response.text(encoding='utf-8')
    except aiohttp.ClientConnectionError:
        log.error('Cannot connect to host kakoyprazdnik.com:443 ssl:default [Connect call failed (\'89.184.89.203\', 443)]')
        return False

    soup = BeautifulSoup(body, 'html.parser')
    mainzona = soup.find('div', id='mainzona')
    holidays: list = []
    for bloktxt in mainzona:
        tags = []
        try:
            name = bloktxt.find('h4').text
            bloktxt_left = bloktxt.find('div', id='bloktxt_left')
            htmltags = bloktxt_left.find_all('a')
            for tag in htmltags:
                tags.append(tag.text)
            holidays.append([name, tags])
        except:
            continue
    
    filtered_holidays = holidays.copy()
    for holiday in holidays:
        if filter_holiday(holiday[1]):
            filtered_holidays.remove(holiday)
    
    with Session(engine) as session:
        results = session.exec(select(Holiday).where(Holiday.day == date.day).where(Holiday.month == date.month))
    
        for saved_holiday in results:
            session.delete(saved_holiday)
            
        for pending_holiday in filtered_holidays:
            holiday = Holiday(name=pending_holiday[0], day=date.day, month=date.month)
            session.add(holiday)
            
        session.commit()
    
    return True
