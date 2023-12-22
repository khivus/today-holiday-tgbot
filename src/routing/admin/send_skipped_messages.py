import datetime

from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router
from src.constants import tzinfo
from src.utility.send_scheduled_messages import send_scheluded_holidays_message


@admin_router.message(Command('send_skipped_messages'))
async def process_send_skipped_messages(message: types.Message) -> None:
    tnow = datetime.datetime.now(tz=tzinfo)
    hour = tnow.hour
    message_text = ''
    
    for h in range(hour + 1):
        success = await send_scheluded_holidays_message(hour=h)
        if success[0] != 0 or success[1] != 0:
            message_text += f'At hour {h}: {success[0]}/{success[1]}\n'
    
    await message.answer(text=message_text)
