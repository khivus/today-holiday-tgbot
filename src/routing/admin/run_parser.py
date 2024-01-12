import datetime

from aiogram import types
from aiogram.filters import Command

from src.constants import Date, tzinfo
from src.routers import admin_router
from src.utility.site_parser import parse_site


@admin_router.message(Command('run_parser'))
async def process_parser(message: types.Message) -> None:
    
    index = message.text.find(' ')
    if index != -1:
        str_date = message.text[index+1:]
        raw_date = str_date.split('.')
        date = Date(day=int(raw_date[0]), month=int(raw_date[1]))
    else:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = Date(day=tnow.day, month=tnow.month)
    
    if await parse_site(date=date):
        message_text = f'Сайт пропаршен в дату: <code>{date.day}.{date.month}</code> и добавлен в бд.'
    else:
        message_text = 'Сайт не удалось пропарсить.'

    await message.answer(text=message_text)
