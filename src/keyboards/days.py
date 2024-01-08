from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class FindDayCallbackData(CallbackData, prefix='Days'):
    chosen_day: int
    chosen_month: int

def build_days_keyboard(chosen_month: int):
    
    if chosen_month in [1, 3, 5, 7, 8, 10, 12]:
        days = 31
    elif chosen_month in [4, 6, 9, 11]:
        days = 30
    else:
        days = 29
    
    builder = InlineKeyboardBuilder()
    for i in range(1, days + 1):
        builder.button(text=f'{i}', callback_data=FindDayCallbackData(chosen_day=i, chosen_month=chosen_month))
    builder.button(text='↩️ Вернуться к выбору', callback_data=FindDayCallbackData(chosen_day=-1, chosen_month=chosen_month))

    builder.adjust(8, 8, 8, days-24, 1)

    return builder.as_markup()
