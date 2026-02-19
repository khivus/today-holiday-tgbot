import datetime
from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session

from src.models.holiday import Holiday
from src.routers import admin_router
from src.constants import engine, tzinfo_msk, Date


@admin_router.message(Command('add_holiday'))
async def process_remove_holiday(message: types.Message) -> None:

    holiday_raw = message.text.removeprefix('/add_holiday').strip()

    if not holiday_raw:
        await message.answer(text="Что добавить то?")
        return

    if '=' in holiday_raw:
        holiday_name, holiday_date_str = holiday_raw.split('=')
        holiday_name = holiday_name.strip()
        holiday_date_str = holiday_date_str.strip()
        holiday_date = [int(part) for part in holiday_date_str.split('.')]
        date = Date(day=holiday_date[0], month=holiday_date[1])
    else:
        holiday_name = holiday_raw
        tnow = datetime.datetime.now(tz=tzinfo_msk)
        date = Date(day=tnow.day, month=tnow.month)

    if not holiday_name:
        await message.answer(text="Пожалуйста, укажите название праздника.")
        return
    
    with Session(engine) as session:
        holiday = Holiday(name=holiday_name, day=date.day, month=date.month)
        session.add(holiday)
        session.commit()

    await message.answer(text=f'Праздник "{holiday_name}" был добавлен в базу данных на дату: {date.day}.{date.month}.')