import datetime

from aiogram import types

from src.keyboards.page_change import PagesCallbackData, build_pages_keyboard
from src.routers import main_router
from src.utility.chat_check import is_group_in_db
from src.utility.page_builder import build_pages
from src.constants import tzinfo, Date


def get_holiday_message(page_index: int, pages: list[str], date: Date | None = None):
    if not date:
        tnow = datetime.datetime.now(tz=tzinfo)
        date = Date(day=tnow.day, month=tnow.month)
    
    max_index = len(pages)
    lbreak: str = '\n'
    msg_start = f'Праздники на {date.day:02}.{date.month:02}:\n{lbreak:->50}'
    msg_end = f'{lbreak:->50}Страница {page_index+1}/{max_index}'
    page = pages[page_index]
    message = msg_start + page + msg_end
    return message


@main_router.callback_query(PagesCallbackData.filter())
async def process_change_pages_callback(query: types.CallbackQuery, callback_data: PagesCallbackData):
    is_group_in_db(chat_id=query.message.chat.id)
    
    date = Date(day=callback_data.day, month=callback_data.month)
    pages = await build_pages(chat_id=query.message.chat.id, date=date)
    max_index = len(pages)
    page_index = callback_data.current_page_index
    new_page_index = min(max(page_index, 0), max_index-1)
    message_text = get_holiday_message(page_index=new_page_index, pages=pages, date=date)
    keyboard = build_pages_keyboard(current_page_index=new_page_index, max_page_index=max_index, date=date)
    
    try:
        if new_page_index == page_index:
            await query.message.edit_text(text=message_text, reply_markup=keyboard)
        else:
            await query.answer()
    except:
        pass