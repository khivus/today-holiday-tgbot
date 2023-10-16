import aiohttp
import datetime

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from user_agent import generate_user_agent

from src.constants import ADMIN, bot
from src.models.holiday import HolidayType, Holiday
from src.constants import engine


async def parse_site() -> None:
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
    new_holidays = 0
    updated_holidays = 0
    skip = False

    with Session(engine) as session:
        results = session.exec(select(Holiday).where(
            Holiday.day == day).where(Holiday.month == month))
        for pending_holiday in elements:
            for saved_holiday in results:
                if saved_holiday.name == pending_holiday[0] and (saved_holiday.years_passed == pending_holiday[2] or saved_holiday.years_passed == None):
                    skip = True
                    break
                elif saved_holiday.name == pending_holiday[0] and saved_holiday.years_passed != pending_holiday[2] and saved_holiday.years_passed != None:
                    saved_holiday.years_passed = pending_holiday[2]
                    session.add(saved_holiday)
                    updated_holidays += 1
                    skip = True
                    break
            if not skip:
                holiday = Holiday(name=pending_holiday[0], type=pending_holiday[1], years_passed=pending_holiday[2], day=day, month=month)
                session.add(holiday)
                new_holidays += 1
            
            skip = False
            
        session.commit()
    
    if new_holidays != 0 or updated_holidays != 0:
        print(f'Added {new_holidays} and updated {updated_holidays} holidays (no:{normal_counter}/co:{country_specific_counter}/ch:{church_counter}/na:{name_day_counter}).')
        msg = 'Сайт успешно пропаршен.\n' \
            f'Добавлено: <code>{new_holidays}</code>\n' \
            f'Обновлено: <code>{updated_holidays}</code>\n' \
            f'Обычные: <code>{normal_counter}</code>\n' \
            f'Национальные: <code>{country_specific_counter}</code>\n' \
            f'Церковные: <code>{church_counter}</code>\n' \
            f'Именины: <code>{name_day_counter}</code>'
        await bot.send_message(chat_id=ADMIN, text=msg)
    else:
        print(f'Site parsed, but holidays are already in db! {new_holidays}/{updated_holidays}')
        return False
    
    return True
