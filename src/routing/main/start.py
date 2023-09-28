from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.constants import engine
from src.models.chat import Chat
from src.routers import main_router
from src.routing.main.holidays import process_holidays


@main_router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    with Session(engine) as session:
        if not session.exec(select(Chat).where(Chat.id == message.chat.id)).all():
            chat = Chat(id=message.chat.id)
            session.add(chat)
            session.commit()
            # TODO Bor
            # TODO Khivus "если хотите узнать информацию о боте, вызовите команду /about"
            await message.answer(text='Вы были успешно добавлены в бота!\n\
                                       Отправьте /holiday чтобы узнать, какой сегодня праздник.')

        else:
            await process_holidays(message)
