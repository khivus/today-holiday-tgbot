from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.constants import engine
from src.models.chat import Chat
from src.routers import main_router
from src.routing.main.holidays import process_holidays
from src.utility.chat_check import chat_check


@main_router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    if not chat_check(chat_id=message.chat.id, migrate_from_chat_id=message.migrate_from_chat_id, migrate_to_chat_id=message.migrate_to_chat_id):
        message_text = 'Я - Какой сегодня праздник бот!\n' \
            'Отправь /holidays чтобы узнать, какой сегодня праздник.\n' \
            'Включить ежедневную авторассылку праздников можно в /settings.\n' \
            'Для вопросов и предложений: @khivus.\n' \
            'Праздники взяты с этого <a href="https://kakoysegodnyaprazdnik.ru/">сайта</a>.\n' \
            'Бот всё ещё в активной разработке, поэтому возможны сбои в работе!'
            
        try:
            await message.answer(text=message_text, disable_web_page_preview=True)
        except:
            pass
        
    else:
        with Session(engine) as session:
            chat = session.exec(select(Chat).where(Chat.id == message.chat.id)).one()
            if chat.banned:
                chat.banned = False
                session.add(chat)
                session.commit()
            await process_holidays(message)
