from datetime import datetime
from aiogram import types

from src.keyboards.page_change import PagesCallbackData, build_pages_keyboard
from src.routers import main_router
from src.page_builder import build_pages


def get_holiday_message(page_index: int, pages: list[str]):
    date = datetime.today()
    max_index = len(pages)
    msg_start = f'Праздники на {date.day:02}.{date.month:02}.{date.year}:\n' \
        '--------------------------------------------------\n'
    msg_end = '--------------------------------------------------\n' \
        f'Страница {page_index+1}/{max_index}'
    page = pages[page_index]
    message = msg_start + page + msg_end
    return message


@main_router.callback_query(PagesCallbackData.filter())
async def process_change_pages_callback(query: types.CallbackQuery, callback_data: PagesCallbackData):
    pages = build_pages(chat_id=query.message.chat.id)
    max_index = len(pages)
    page_index = callback_data.current_page_index
    new_page_index = min(max(page_index, 0), max_index-1)
    message_text = get_holiday_message(page_index=new_page_index, pages=pages)
    keyboard = build_pages_keyboard(current_page_index=new_page_index, max_page_index=max_index)
    if new_page_index == page_index:
        await query.message.edit_text(text=message_text, reply_markup=keyboard)
    else:
        await query.answer()