from src.constants import ADMIN, bot
from src.utility.print_timestamp_builder import print_with_timestamp


async def send_successful_start_message():
    print_with_timestamp('Bot started polling...')
    await bot.send_message(chat_id=ADMIN, text='Бот успешно запущен.')
