from aiogram import types
from sqlmodel import Session, select

from src.constants import engine
from src.keyboards.hours import HourCallbackData, build_hours_keyboard
from src.keyboards.settings import SettingType, SettingsCallbackData, build_settings_keyboard
from src.models.chat import Chat
from src.routers import main_router
from src.routing.main.settings import get_text
from src.utility.chat_check import is_group_in_db


@main_router.callback_query(SettingsCallbackData.filter())
async def process_setting_callback(query: types.CallbackQuery, callback_data: SettingsCallbackData):
    is_group_in_db(chat_id=query.message.chat.id)
    reply_markup = None
    
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(Chat.id == query.message.chat.id)).one()

        if callback_data.type == SettingType.MAILING_ENABLED:
            chat.mailing_enabled = not chat.mailing_enabled
            msg = get_text(additional_text=f'Рассылка теперь <code>{"включена" if chat.mailing_enabled else "выключена"}</code>.\n', chat=chat)

        elif callback_data.type == SettingType.MAILING_TIME:
            msg = 'Выберите час в который вы хотите получать рассылку:'
            reply_markup = build_hours_keyboard()

        elif callback_data.type == SettingType.SEND_CHURCH_HOLIDAYS:
            chat.send_church_holidays = not chat.send_church_holidays
            msg = get_text(additional_text=f'Церковные праздники теперь <code>{"включены" if chat.send_church_holidays else "выключены"}</code>.\n', chat=chat)

        elif callback_data.type == SettingType.SEND_COUNTRY_SPECIFIC:
            chat.send_country_specific = not chat.send_country_specific
            msg = get_text(additional_text=f'Национальные праздники теперь <code>{"включены" if chat.send_country_specific else "выключены"}</code>.\n', chat=chat)

        elif callback_data.type == SettingType.RESET:
            chat.mailing_enabled = False
            chat.mailing_time = 8
            chat.send_church_holidays = True
            chat.send_country_specific = True
            msg = get_text(additional_text='Все настройки были сброшены до заводских.\n', chat=chat)
        
        else:
            msg = get_text(chat=chat)

        session.add(chat)
        session.commit()

    if not reply_markup:
        reply_markup = build_settings_keyboard(chat_id=query.message.chat.id)
    
    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except:
        pass


@main_router.callback_query(HourCallbackData.filter())
async def process_hours_callback(query: types.CallbackQuery, callback_data: HourCallbackData):
    is_group_in_db(chat_id=query.message.chat.id)
    
    hour = callback_data.chosen_hour
    
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(Chat.id == query.message.chat.id)).one()
        
        if hour == 24: # If you go back to settings
            msg = get_text(chat=chat)
        else:
            chat.mailing_time = hour
            session.add(chat)
            session.commit()
            msg = get_text(additional_text=f'Время рассылки было поменяно на: <code>{chat.mailing_time}:00</code>.\n', chat=chat)

        session.add(chat)
        session.commit()
            
    reply_markup = build_settings_keyboard(chat_id=query.message.chat.id)

    try:
        await query.message.edit_text(text=msg, reply_markup=reply_markup)
    except:
        pass
