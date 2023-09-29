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
            msg = 'Я - Какой сегодня праздник бот!\n' \
                'Отправь /holiday чтобы узнать, какой сегодня праздник.\n' \
                'Включить ежедневную авторассылку праздников можно в /settings.\n' \
                'Для вопросов и предложений: @khivus.\n' \
                'Данные праздников взяты с этого <a href="https://kakoysegodnyaprazdnik.ru/">сайта</a>.'
                
            await message.answer(text=msg)

        else:
            await process_holidays(message)
