from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.constants import VERSION
from src.utility.chat_check import chat_check


@main_router.message(Command("about"))
async def process_about(message: types.Message) -> None:
    chat_check(chat_id=message.chat.id, migrate_from_chat_id=message.migrate_from_chat_id, migrate_to_chat_id=message.migrate_to_chat_id)
    msg = 'Я - Какой сегодня праздник бот!\n' \
        'Для вопросов и предложений: @khivus\n' \
        f'Версия бота: <code>{VERSION}</code>\n' \
        'Исходный код открытый и есть на <a href="https://github.com/khivus/today-holiday-tgbot">гитхабе</a>.\n' \
        'Праздники взяты с этого <a href="https://kakoysegodnyaprazdnik.ru/">сайта</a>.'
        
    try:
        await message.answer(text=msg, disable_web_page_preview=True)
    except:
        print('funny')