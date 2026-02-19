from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.models.holiday import Holiday
from src.routers import admin_router
from src.constants import engine


@admin_router.message(Command('remove_holiday'))
async def process_remove_holiday(message: types.Message) -> None:

    holiday_name = message.text.removeprefix('/remove_holiday').strip()
    
    if not holiday_name:
        await message.answer(text="Пожалуйста, укажите название праздника для удаления.")
        return
    
    with Session(engine) as session:
        # Удаляем праздники с таким же названием
        results = session.exec(select(Holiday).where(Holiday.name == holiday_name)).all()
        
        for saved_holiday in results:
            session.delete(saved_holiday)
        
        session.commit()

    await message.answer(text=f'Праздник "{holiday_name}" был удален из базы данных.')
