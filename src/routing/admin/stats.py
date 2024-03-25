import datetime

from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.models.chat import Chat
from src.models.holiday import Holiday
from src.routers import admin_router
from src.constants import VERSION, engine, tzinfo


@admin_router.message(Command('stats'))
async def process_stats(message: types.Message) -> None:
    
    total_chats = 0
    total_uses = 0
    total_with_mailing = 0
    total_holidays = 0
    
    tnow = datetime.datetime.now(tz=tzinfo)
    
    with Session(engine) as session:
        holidays = session.exec(select(Holiday)).all()
        chats = session.exec(select(Chat)).all()
        for chat in chats:
            total_chats += 1
            total_uses += chat.uses
            total_with_mailing += chat.mailing_enabled
        total_holidays = len(holidays)
            
    message_text = f'Версия бота: <code>{VERSION}</code>\n' \
        f'Время и дата сейчас: <code>{tnow.day:02}.{tnow.month:02}.{tnow.year} {tnow.hour:02}:{tnow.minute:02}:{tnow.second:02}</code>\n\n' \
        f'Всего чатов: <code>{total_chats}</code>\n' \
        f'Всего использований: <code>{total_uses}</code>\n' \
        f'Всего с рассылкой: <code>{total_with_mailing}</code>\n' \
        f'Всего праздников: <code>{total_holidays}</code>\n'
            
    await message.answer(text=message_text)
