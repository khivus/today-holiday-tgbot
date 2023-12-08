from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.constants import VERSION
from src.utility.chat_check import is_group_in_db


@main_router.message(Command("about"))
async def process_about(message: types.Message) -> None:
    is_group_in_db(chat_id=message.chat.id)
    msg = 'Я - Какой сегодня праздник бот!\n' \
        'Для вопросов и предложений: @reveverless\n' \
        f'Версия бота: <code>{VERSION}</code>\n' \
        'Праздники взяты с этого <a href="https://kakoysegodnyaprazdnik.ru/">сайта</a>.'
        
    try:
        await message.answer(text=msg, disable_web_page_preview=True)
    except:
        print('funny')