from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.constants import engine
from src.models.chat import Chat
from src.routers import main_router
from src.routing.main.message.holidays import process_holidays


@main_router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    with Session(engine) as session:
        if not session.exec(select(Chat).where(Chat.id == message.chat.id)).all():
            user = Chat(id=message.chat.id)
            session.add(user)
            session.commit()
            reply_text = 'User added'

        else:
            await process_holidays(message)
            reply_text = 'Holiday list'

    await message.answer(text=reply_text)
