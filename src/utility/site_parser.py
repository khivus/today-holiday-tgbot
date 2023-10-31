import aiohttp
import datetime

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from user_agent import generate_user_agent

from src.constants import ADMIN, bot
from src.models.holiday import HolidayType, Holiday
from src.constants import engine
from src.utility.print_builder import better_print


async def parse_site(additional_info: str = '') -> None:
    time_start = datetime.datetime.now()
    
    url = 'https://kakoysegodnyaprazdnik.ru/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
            body = await response.text(encoding='utf-8')

    soup = BeautifulSoup(body, 'html.parser')
    listl = soup.find('div', class_='listing_wr')

    elements: list[str] = []
    i = 0
    
    normal_counter = 0
    church_counter = 0
    country_specific_counter = 0
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
                        normal_counter += 1
                    case 1: 
                        holiday_type = HolidayType.church
                        church_counter += 1
                    case 2: 
                        holiday_type = HolidayType.country_specific
                        country_specific_counter += 1
                    case 3: 
                        holiday_type = HolidayType.name_day
                        name_day_counter += 1
                    case default: raise Exception('Holiday type index overflow!')

                elements.append((holiday_name, holiday_type, years_passed))

    today = datetime.date.today()
    day = today.day
    month = today.month
    new_holidays = len(elements)

    with Session(engine) as session:
        results = session.exec(select(Holiday).where(
            Holiday.day == day).where(Holiday.month == month))
        
        for saved_holiday in results:
            session.delete(saved_holiday)
            
        for pending_holiday in elements:
            holiday = Holiday(name=pending_holiday[0], type=pending_holiday[1], years_passed=pending_holiday[2], day=day, month=month)
            session.add(holiday)
            
        session.commit()
    
    time_end = datetime.datetime.now()
    time_diff = int((time_end - time_start).total_seconds() * 1000)
    
    if new_holidays != 0:
        better_print(text=f'{additional_info}Added {new_holidays} holidays (no:{normal_counter}/co:{country_specific_counter}/ch:{church_counter}/na:{name_day_counter})', time_diff=time_diff)
        msg = 'Сайт успешно пропаршен.\n' \
            f'Добавлено: <code>{new_holidays}</code>\n' \
            f'Обычные: <code>{normal_counter}</code>\n' \
            f'Национальные: <code>{country_specific_counter}</code>\n' \
            f'Церковные: <code>{church_counter}</code>\n' \
            f'Именины: <code>{name_day_counter}</code>'
        await bot.send_message(chat_id=ADMIN, text=msg)
    else:
        better_print(text=f'{additional_info}Site don\'t parsed!', time_diff=time_diff)
        return False
    
    return True
