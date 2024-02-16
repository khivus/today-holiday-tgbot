import aiohttp
import asyncio

from user_agent import generate_user_agent
from bs4 import BeautifulSoup

with open('logs.txt', 'w', encoding='utf-8') as file:
    file.write('PARSE SITE LOGS START')

async def parse_all():
    holidays: list = []
    months: list = [
        'yanvarya',
        'fevralya',
        'marta',
        'aprelya',
        'maya',
        'ijunya',
        'ijulya',
        'avgusta',
        'sentyabrya',
        'oktyabrya',
        'noyabrya',
        'dekabrya'
    ]
    for month in months:
        chosen_month = months.index(month) + 1
        if chosen_month in [1, 3, 5, 7, 8, 10, 12]:
            days = 31
        elif chosen_month in [4, 6, 9, 11]:
            days = 30
        else:
            days = 29
        for day in range(1, days + 1):
            holidays.append(await parse_page(month=month, day=day))
            print(f'done {month} {day}')
            with open('logs.txt', 'a', encoding='utf-8') as file:
                to_file = f'\ndone {month} {day} \n {holidays[len(holidays)-1]}\n'
                file.write(to_file)
            await asyncio.sleep(3)
    just_names: list = []
    tag_list: list = []
    for day in holidays:
        for holiday in day:
            name = holiday[0]
            just_names.append(name)
            tags = holiday[1]
            for tag in tags:
                if tag not in tag_list:
                    tag_list.append(tag)

    with open('holidays.txt', 'w', encoding='utf-8') as file:
        country_str = '\n'.join(just_names)
        file.write(country_str)
    with open('tags.txt', 'w', encoding='utf-8') as file:
        tagss = '\n'.join(tag_list)
        file.write(tagss)
    print('done')
    
def filter_holiday(tags: list):
    filterd_tags = tags.copy()
    filter_tags = ['Народные', 'Праздники Беларуси', 'Праздники России', 'Праздники Украины', 'Церковные', 'Православные', 'Католические', 'Национальные', 'Праздники США', 'Лютеранские', 'Конституционные', 'Дни памяти', 'Посты', 'Мусульманские']
    for tag in tags:
        if tag in filter_tags:
            filterd_tags.remove(tag)
    if filterd_tags == []:
        return True
    else:
        return False
    

async def parse_page(month: str | None = None, day: int | None = None):
    if day and month:
        url = f'https://kakoyprazdnik.com/den/{day}-{month}'
    else:
        url = 'https://kakoyprazdnik.com/'

    async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
                body = await response.text(encoding='utf-8')

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
    print(holidays)
    print(filtered_holidays)

    return holidays
        
if __name__ == '__main__':
     asyncio.run(parse_page())