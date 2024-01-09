from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class CancelCallbackData(CallbackData, prefix='Cancel'):
    cancel: bool

def build_cancel_keyboard():
    
    builder = InlineKeyboardBuilder()
    
    builder.button(text='↩️ Вернуться назад', callback_data=CancelCallbackData(cancel=True))

    return builder.as_markup()