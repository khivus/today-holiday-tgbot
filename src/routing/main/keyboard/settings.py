# from aiogram.filters.callback_data import CallbackData
# from aiogram.utils.keyboard import InlineKeyboardBuilder


# class SettingsCallbackData(CallbackData, prefix='setup'):
#     time = 'time'
#     enabled = 'enable'
#     only_rus = 'rus only'
#     name_day = 'name days'
#     day_of_remembrance = 'days of remembrance'


# def build_settings_keyboard():
#     builder = InlineKeyboardBuilder()

#     builder.button(text='Enable', callback_data='ENABLE')
#     builder.button(text='Set up time', callback_data='TIME')
#     builder.button(text='Rus only', callback_data=SettingsCallbackData(only_rus='rus only'))
#     builder.button(text='Name days', callback_data=SettingsCallbackData(name_day='name days'))
#     builder.button(text='Days of rememb', callback_data=SettingsCallbackData(day_of_remembrance='days of remembrance'))

#     builder.adjust(2, 2, 1)

#     return builder.as_markup()
