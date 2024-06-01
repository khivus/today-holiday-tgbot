from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.utility.chat_check import is_group_in_db


@main_router.message(Command("help"))
async def process_help(message: types.Message) -> None:
    is_group_in_db(chat_id=message.chat.id)
    message_text = 'Список команд и их краткое описание:\n' \
            '/start - При первом использовании отправляет сообщение из /about, далее /holidays.\n' \
            '/holidays - Отправляет список сегодняшних праздников.\n' \
            '/tomorrow - Отправляет список завтрашних праздников.\n' \
            '/find_holiday - Поиск праздника по дню или названию.\n' \
            '/settings - Настройки ежедневной рассылки и категорий праздников.\n' \
            '/about - Информация о боте.\n' \
            '/help - Эта команда.\n' \
            'Так же можно получать список праздников, просто написав: сегодня, завтра, послезавтра, вчера, позавчера. К тому же можно писать день недели или дату(день.месяц), на которую вам интересен список праздников.'
        
    try:
        await message.answer(text=message_text)
    except:
        pass