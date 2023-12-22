import datetime

from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router
from src.constants import tzinfo, bot, ADMIN

@admin_router.message(Command('create_backup'))
async def create_db_backup(message: types.Message = None) -> None:
    db_file_path = 'resources/database.db'
    tnow = datetime.datetime.now(tz=tzinfo)
    new_file_name = f'backup_{tnow.day:02}_{tnow.month:02}_{tnow.year}.db'
    
    file = types.FSInputFile(f'{db_file_path}', f'{new_file_name}')
    await bot.send_document(chat_id=ADMIN, document=file)