from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class PagesCallbackData(CallbackData, prefix='page'):
    current_page_index: int


def build_pages_keyboard(current_page_index):
    builder = InlineKeyboardBuilder()
    # TODO Khivus добавить еще 2 клавы на первую/последнюю страницу
    # TODO Bor ASCII стрелочки красиво
    builder.button(
        text='⬅️', callback_data=PagesCallbackData(current_page_index=current_page_index - 1))
    builder.button(
        text='➡️', callback_data=PagesCallbackData(current_page_index=current_page_index + 1))

    return builder.as_markup()
