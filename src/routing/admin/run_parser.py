from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router
from src.utility.calculate_movable_dates import calculate_movable_dates


@admin_router.message(Command('run_parser'))
async def process_parser(message: types.Message) -> None:
    
    await calculate_movable_dates()

    await message.answer(text="Даты праздников пересчитаны.")
