import json

from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router
from src.constants import ADMIN, VERSION, bot, daily_json_template


@admin_router.message(Command('dstats'))
async def process_daily_stats(message: types.Message | None = None) -> None:
    
    with open('daily_stats.json', 'r') as file:
        daily_data = json.load(file)
    
    message_text = f'Ежедневная статистика:\n' \
        f'Версия бота: <code>{VERSION}</code>\n' \
        f'Новых чатов: <code>{daily_data["new_chats"]}</code>\n' \
        f'Использований: <code>{daily_data["uses"]}</code>\n' \
        f'Успешных рассылок: <code>{daily_data["succeeded_messages"]}/{daily_data["all_scheduled_messages"]}</code>'
    
    if not message:
        with open('daily_stats.json', 'w') as file:
            json.dump(daily_json_template, file)
    
    await bot.send_message(chat_id=ADMIN, text=message_text)
