from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class HourCallbackData(CallbackData, prefix='meow'):
    chosen_hour: int


def build_hours_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(24):
        builder.button(text=f'{i}', callback_data=HourCallbackData(chosen_hour=i))
    builder.button(text='↩️ Вернуться в настройки', callback_data=HourCallbackData(chosen_hour=24))

    builder.adjust(6, 6, 6, 6, 1)

    return builder.as_markup()
