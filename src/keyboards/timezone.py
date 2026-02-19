from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class TimezoneCallbackData(CallbackData, prefix='meow2'):
    chosen_timezone: int

def build_timezone_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(-12, 15):
        builder.button(text=f'{i}', callback_data=TimezoneCallbackData(chosen_timezone=i))
    builder.button(text='↩️ Вернуться к настройкам', callback_data=TimezoneCallbackData(chosen_timezone=13))

    builder.adjust(7, 7, 7, 6, 1)

    return builder.as_markup()
