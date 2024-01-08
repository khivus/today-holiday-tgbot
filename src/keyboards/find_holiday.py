import enum

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class FindType(enum.Enum):
    BY_DATE = 'by_date'
    BY_NAME = 'by_name'

class FindHolidayCallbackData(CallbackData, prefix='FindHoliday'):
    find_by: FindType

def build_find_holiday_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.button(text='🗓️ Найти по дате', callback_data=FindHolidayCallbackData(find_by=FindType.BY_DATE))
    builder.button(text='📝 Найти по названию', callback_data=FindHolidayCallbackData(find_by=FindType.BY_NAME))

    builder.adjust(1, 1)

    return builder.as_markup()
