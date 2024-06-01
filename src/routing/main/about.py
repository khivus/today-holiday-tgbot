from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.utility.chat_check import is_group_in_db


@main_router.message(Command("about"))
async def process_about(message: types.Message) -> None:
    is_group_in_db(chat_id=message.chat.id)
    message_text = 'Я - Какой сегодня праздник бот!\n' \
            'Отправь /holidays чтобы узнать, какой сегодня праздник.\n' \
            'Если хочешь узнать какие завтра праздники, используй /tomorrow.\n' \
            'Включить ежедневную авторассылку (по МСК) праздников можно в /settings.\n' \
            'Для вопросов и предложений: @khivus.\n' \
            'Так же можно получать список праздников, просто написав: сегодня, завтра, послезавтра, вчера, позавчера. К тому же можно писать день недели или дату(день.месяц), на которую вам интересен список праздников.\n' \
            'Бот всё ещё в активной разработке, поэтому возможны сбои в работе!'
        
    try:
        await message.answer(text=message_text, disable_web_page_preview=True)
    except:
        pass