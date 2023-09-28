import enum
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class SettingType(enum.Enum):
    MAILING_ENABLED = 'mailing_enabled'
    MAILING_TIME = 'mailing_time'
    SEND_CHURCH_HOLIDAYS = 'send_church_holidays'
    SEND_COUNTRY_SPECIFIC = 'send_country_specific'
    SEND_NAME_DAYS = 'send_name_days'
    RESET = 'reset'


class SettingsCallbackData(CallbackData, prefix='generate'):
    type: SettingType


def build_settings_keyboard():
    builder = InlineKeyboardBuilder()
    # TODO Bor x6
    # TODO Khivus придумать как ставить галочки и крестики в кнопки вместо + и -
    builder.button(text='+- Рассылка', callback_data=SettingsCallbackData(
        type=SettingType.MAILING_ENABLED))
    builder.button(text='⏰ Время рассылки', callback_data=SettingsCallbackData(
        type=SettingType.MAILING_TIME))
    builder.button(text='+- Церковные', callback_data=SettingsCallbackData(
        type=SettingType.SEND_CHURCH_HOLIDAYS))
    builder.button(text='+- Национальные', callback_data=SettingsCallbackData(
        type=SettingType.SEND_COUNTRY_SPECIFIC))
    builder.button(text='+- Именины', callback_data=SettingsCallbackData(
        type=SettingType.SEND_NAME_DAYS))
    builder.button(text='Сбросить настройки до заводских', callback_data=SettingsCallbackData(
        type=SettingType.RESET))

    builder.adjust(1, 2, 2, 1)

    return builder.as_markup()
