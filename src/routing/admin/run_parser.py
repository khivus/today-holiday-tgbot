from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router
from src.site_parser import parse_site


@admin_router.message(Command('run_parser'))
async def process_start(message: types.Message) -> None:
    # TODO Bor
    if await parse_site():
        message_text = 'Site parsed and added to db.'
    else:
        message_text = 'Site don\'t parsed'

    await message.answer(text=message_text)
