from src.constants import ADMIN, bot


async def send_successful_start_message():
    print('Bot started polling...')
    await bot.send_message(chat_id=ADMIN, text='Бот успешно запущен.')
