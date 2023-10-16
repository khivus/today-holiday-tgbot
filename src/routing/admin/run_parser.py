from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router
from src.site_parser import parse_site


@admin_router.message(Command('run_parser'))
async def process_parser(message: types.Message) -> None:
    if await parse_site():
        message_text = 'Сайт пропаршен и добавлен в БД.'
    else:
        message_text = 'Сайт не удалось пропарсить или праздники уже есть в базе данных.'

    await message.answer(text=message_text)
