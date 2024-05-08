import datetime
from aiogram import types

from src.constants import Date
from src.keyboards.page_change import build_pages_keyboard
from src.routers import main_router
from src.routing.main.holidays import process_holidays
from src.routing.main.tomorrow import process_tomorrow
from src.utility.chat_check import is_group_in_db
from src.utility.page_builder import build_pages, get_holiday_message


# @main_router.message()
# async def process_about(message: types.Message) -> None:
    
    # if message.text == 'сегодня':
    #     await process_holidays(message=message)
    # elif message.text == 'завтра':
    #     await process_tomorrow(message=message)
    # elif '.' in message.text:
    #     is_group_in_db(chat_id=message.chat.id)

    #     raw_date: list = message.text.split('.')
    #     date = Date(day=int(raw_date[0]), month=int(raw_date[1]))

    #     pages = await build_pages(date=date)
    #     message_text = get_holiday_message(page_index=0, pages=pages, date=date)
    #     keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages), date=date)

    #     try:
    #         await message.answer(text=message_text, reply_markup=keyboard)
    #     except:
    #         pass