from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router


@admin_router.message(Command('ahelp'))
async def process_send_skipped_messages(message: types.Message) -> None:
    message_text = 'Список админских команд:\n' \
                '/send_skipped_messages\n' \
                '/stats\n' \
                '/dstats\n' \
                '/run_parser\n' \
                '/create_backup'
    
    await message.answer(text=message_text)
