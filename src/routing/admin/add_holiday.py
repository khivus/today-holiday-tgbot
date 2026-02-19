from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session

from src.models.holiday import Holiday
from src.routers import admin_router
from src.constants import engine


@admin_router.message(Command('add_holiday'))
async def process_remove_holiday(message: types.Message) -> None:

    holiday_raw = message.text.removeprefix('/add_holiday').strip()

    if not holiday_raw:
        await message.answer(text="Что добавить то?")
        return

    holiday_name, holiday_date_str = holiday_raw.split('=')
    holiday_name = holiday_name.strip()
    holiday_date_str = holiday_date_str.strip()
    holiday_date = [int(part) for part in holiday_date_str.split('.')]
    
    if not holiday_name or not holiday_date_str:
        await message.answer(text="Пожалуйста, укажите название праздника или дату для добавления.")
        return
    
    with Session(engine) as session:
        holiday = Holiday(name=holiday_name, day=holiday_date[0], month=holiday_date[1])
        session.add(holiday)
        session.commit()

    await message.answer(text=f'Праздник "{holiday_name}" был добавлен в базу данных на дату: {holiday_date_str}.')