from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MonthsCallbackData(CallbackData, prefix='Months'):
    chosen_month: int

def build_months_keyboard():
    
    builder = InlineKeyboardBuilder()
    
    for i in range(1, 13):
        builder.button(text=f'{i}', callback_data=MonthsCallbackData(chosen_month=i))
    builder.button(text='↩️ Вернуться назад', callback_data=MonthsCallbackData(chosen_month=-1))

    builder.adjust(6, 6, 1)

    return builder.as_markup()
