from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.models.chat import Chat
from src.models.holiday import Holiday, HolidayType
from src.routers import admin_router
from src.constants import VERSION, engine


@admin_router.message(Command('stats'))
async def process_stats(message: types.Message) -> None:
    
    total_chats = 0
    total_uses = 0
    total_with_mailing = 0
    total_holidays = 0
    total_normal = 0
    total_country = 0
    total_church = 0
    
    with Session(engine) as session:
        holidays = session.exec(select(Holiday)).all()
        chats = session.exec(select(Chat)).all()
        for chat in chats:
            total_chats += 1
            total_uses += chat.uses
            total_with_mailing += chat.mailing_enabled
        for holiday in holidays:
            total_holidays += 1
            if holiday.type == HolidayType.normal: total_normal += 1
            elif holiday.type == HolidayType.country_specific: total_country += 1
            elif holiday.type == HolidayType.church: total_church += 1
            
    message_text = f'Версия бота: <code>{VERSION}</code>\n' \
        f'Всего чатов: <code>{total_chats}</code>\n' \
        f'Всего использований: <code>{total_uses}</code>\n' \
        f'Всего с рассылкой: <code>{total_with_mailing}</code>\n' \
        f'Всего праздников: <code>{total_holidays}</code>\n' \
        f'Всего нормальных: <code>{total_normal}</code>\n' \
        f'Всего национальных: <code>{total_country}</code>\n' \
        f'Всего церковных: <code>{total_church}</code>' \
            
    await message.answer(text=message_text)
