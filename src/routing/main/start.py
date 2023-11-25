from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.routing.main.holidays import process_holidays
from src.utility.chat_check import is_group_in_db
from src.utility.json_update import json_update


@main_router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    if not is_group_in_db(chat_id=message.chat.id):
        message_text = 'Я - Какой сегодня праздник бот!\n' \
            'Отправь /holidays чтобы узнать, какой сегодня праздник.\n' \
            'Включить ежедневную авторассылку праздников можно в /settings.\n' \
            'Для вопросов и предложений: @khivus.\n' \
            'Праздники взяты с этого <a href="https://kakoysegodnyaprazdnik.ru/">сайта</a>.\n' \
            'Бот всё ещё в активной разработке, поэтому возможны сбои в работе!'
        
        json_update('new_chats')
        
        try:
            await message.answer(text=message_text, disable_web_page_preview=True)
        except:
            pass
        
    else:
        await process_holidays(message)
