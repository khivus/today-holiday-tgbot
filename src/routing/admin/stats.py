from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.models.chat import Chat
from src.routers import admin_router
from src.constants import VERSION, engine


@admin_router.message(Command('stats'))
async def process_stats(message: types.Message) -> None:
    total_chats = 0
    total_uses = 0
    total_with_mailing = 0
    with Session(engine) as session:
        chats = session.exec(select(Chat)).all()
        for chat in chats:
            total_chats += 1
            total_uses += chat.uses
            total_with_mailing += 1
    message_text = f'Версия бота: <code>{VERSION}</code>\n' \
        f'Всего чатов: <code>{total_chats}</code>\n' \
        f'Всего использований: <code>{total_uses}</code>\n' \
        f'Всего с рассылкой: <code>{total_with_mailing}</code>'
    await message.answer(text=message_text)
