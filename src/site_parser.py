import aiohttp
from bs4 import BeautifulSoup
from user_agent import generate_user_agent


async def parse_site():
    url = 'https://kakoysegodnyaprazdnik.ru/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers={'User-Agent': generate_user_agent()}) as response:
            body = await response.text(encoding='utf-8')

    soup = BeautifulSoup(body, 'html.parser')
    accepted = soup.find('div', itemprop="acceptedAnswer")
    suggested = soup.find_all('div', itemprop='suggestedAnswer')
    elements: list[str] = []

    for element in [accepted] + suggested:
        holiday_name = element.find('span', itemprop='text').text
        years = element.find('span', class_='super')
        holiday = f'- {holiday_name}'
        if years is not None:
            holiday += f' ({years.text})'

        elements.append(holiday)

    text = '\n'.join(elements)

    return text
