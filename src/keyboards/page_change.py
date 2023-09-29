from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class PagesCallbackData(CallbackData, prefix='page'):
    current_page_index: int


def build_pages_keyboard(current_page_index: int, max_page_index: int = 4):
    if max_page_index == 1:
        return None
    
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text=f'{"⬅️" if current_page_index > 0 else "❌"}', callback_data=PagesCallbackData(current_page_index=current_page_index - 1))
    builder.button(
        text=f'{"➡️" if current_page_index < (max_page_index - 1) else "❌"}', callback_data=PagesCallbackData(current_page_index=current_page_index + 1))

    return builder.as_markup()
