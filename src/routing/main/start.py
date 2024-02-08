from aiogram import types
from aiogram.filters import Command

from src.routers import main_router
from src.routing.main.about import process_about
from src.routing.main.holidays import process_holidays
from src.utility.chat_check import is_group_in_db
from src.utility.json_update import json_update


@main_router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    if not is_group_in_db(chat_id=message.chat.id):
        json_update('new_chats')
        await process_about(message=message)
        
    else:
        await process_holidays(message=message)
