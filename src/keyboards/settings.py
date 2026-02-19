import enum

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from sqlmodel import Session, select

from src.constants import engine
from src.models.chat import Chat


class SettingType(enum.Enum):
    MAILING_ENABLED = 'mailing_enabled'
    MAILING_TIME = 'mailing_time'
    RESET = 'reset'
    TIMEZONE = 'timezone'

class SettingsCallbackData(CallbackData, prefix='generate'):
    type: SettingType

def build_settings_keyboard(chat_id: int):
    builder = InlineKeyboardBuilder()
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
        
        builder.button(text=f'{"✅" if chat.mailing_enabled else "❌"} Рассылка', callback_data=SettingsCallbackData(type=SettingType.MAILING_ENABLED))
        builder.button(text=f'⏰ Время рассылки: {chat.mailing_time}', callback_data=SettingsCallbackData(type=SettingType.MAILING_TIME))
        builder.button(text=f'🌍 Часовой пояс: UTC{"+" if chat.timezone >=0 else "-"}{chat.timezone}', callback_data=SettingsCallbackData(type=SettingType.TIMEZONE))
        builder.button(text='🔄 Сбросить настройки до заводских', callback_data=SettingsCallbackData(type=SettingType.RESET))

    builder.adjust(1, 2, 1)

    return builder.as_markup()
