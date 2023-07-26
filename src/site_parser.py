import aiohttp
import re
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from src.models.holiday import HolidayType


async def parse_site():
    url = 'https://kakoysegodnyaprazdnik.ru/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
            body = await response.text(encoding='utf-8')

    soup = BeautifulSoup(body, 'html.parser')
    listl = soup.find('div', class_='listing_wr')

    elements: list[str] = []
    i = 0

    for element in listl:
        attributes = element.attrs
        dicts = [{'class': ['hr-hr_leto']}, {'class': ['hr-hr_vesna']},
                 {'class': ['hr-hr_winter']}, {'class': ['hr-hr_osen']}, {'id': 'prin'}]
        if attributes in dicts:
            i += 1

        elif element.find('span', itemprop='text'):
            holiday_name = element.find('span', itemprop='text').text

            years = element.find('span', class_='super')
            if years is not None:
                years_passed = str(years.text)
            else:
                years_passed = None

            match i:
                case 1:
                    holiday_type = HolidayType.church
                case 2:
                    holiday_type = HolidayType.country_specific
                case 3:
                    holiday_type = HolidayType.name_day
                case default:
                    holiday_type = HolidayType.normal

            if re.match(r'(международный|всемирный|всенародный).*', holiday_name.lower()):
                holiday_type = HolidayType.international

            # elif re.match(r'.*(славянский|святого|иконы|памяти).*', holiday_low):
            #     holiday_type = HolidayType.church
            # elif re.match(r'.* - .*', holiday_low):
            #     holiday_type = HolidayType.country_specific
            # elif re.match(r'.*(именины|плакальщик).*', holiday_low):
            #     holiday_type = HolidayType.name_day

            elements.append((holiday_type, holiday_name, years_passed))
            print(holiday_type, '|', holiday_name, '|', years_passed)

    # return elements
