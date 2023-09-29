from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.constants import VERSION


@main_router.message(Command("about"))
async def process_about(message: types.Message) -> None:
    msg = 'Я - Какой сегодня праздник бот!\n' \
        'Для вопросов и предложений: @khivus\n' \
        f'Версия бота: <code>{VERSION}</code>\n' \
        'Исходный код открытый и есть на <a href="https://github.com/khivus/today-holiday-tgbot">гитхабе</a>.\n' \
        'Данные праздников взяты с этого <a href="https://kakoysegodnyaprazdnik.ru/">сайта</a>.'

    await message.answer(text=msg, disable_web_page_preview=True)