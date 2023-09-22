from aiogram import types

from src.keyboards.page_change import PagesCallbackData, build_pages_keyboard
from src.routers import main_router
from src.routing.main.message.holidays import build_pages


@main_router.callback_query(PagesCallbackData.filter())
async def process_change_pages_callback(query: types.CallbackQuery, callback_data: PagesCallbackData):
    pages = build_pages(message=query.message)
    max_index = len(pages)
    page_index = callback_data.current_page_index
    new_page_index = min(max(page_index, 0), max_index-1)
    page = pages[new_page_index]
    keyboard = build_pages_keyboard(new_page_index)
    if new_page_index == page_index:
        await query.message.edit_text(page, reply_markup=keyboard)
