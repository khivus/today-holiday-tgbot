import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from src.constants import tzinfo_0, Date
from src.utility.chat_timezone import get_chat_timezone

class PagesCallbackData(CallbackData, prefix='page'):
    current_page_index: int
    day: int
    month: int

def build_pages_keyboard(current_page_index: int, max_page_index: int = 4, date: Date | None = None, chat_id: int | None = None):
    if max_page_index == 1:
        return None
    
    if not date:
        tnow = datetime.datetime.now(tz=get_chat_timezone(chat_id=chat_id)) if chat_id else datetime.datetime.now(tz=tzinfo_0)
        date = Date(day=tnow.day, month=tnow.month)
        
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text=f'{"⬅️" if current_page_index > 0 else "❌"}', callback_data=PagesCallbackData(current_page_index=current_page_index - 1, day=date.day, month=date.month))
    builder.button(
        text=f'{"➡️" if current_page_index < (max_page_index - 1) else "❌"}', callback_data=PagesCallbackData(current_page_index=current_page_index + 1, day=date.day, month=date.month))

    return builder.as_markup()
