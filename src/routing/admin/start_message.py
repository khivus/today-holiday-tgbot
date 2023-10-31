from src.constants import ADMIN, bot
from src.utility.print_builder import better_print


async def send_successful_start_message():
    better_print(text='Bot started polling...')
    await bot.send_message(chat_id=ADMIN, text='Бот успешно запущен.')
