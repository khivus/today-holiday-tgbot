from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select
from src.models.chat import Chat

from src.routers import admin_router
from src.constants import engine


@admin_router.message(Command('stats'))
async def process_start(message: types.Message) -> None:
    total_chats = 0
    total_uses = 0
    with Session(engine) as session:
        chats = session.exec(select(Chat)).all()
        for chat in chats:
            total_chats += 1
            total_uses += chat.uses
    # TODO Bor
    message_text = f'Total chats: <code>{total_chats}</code>\n' \
        f'Total uses: <code>{total_uses}</code>'
    await message.answer(text=message_text)
