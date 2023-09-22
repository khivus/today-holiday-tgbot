from aiogram import types
from sqlmodel import Session, select

from src.constants import engine
from src.keyboards.hours import HourCallbackData, build_hours_keyboard
from src.keyboards.settings import SettingType, SettingsCallbackData, build_settings_keyboard
from src.models.chat import Chat
from src.routers import main_router
from src.routing.main.message.settings import get_text

# TODO: Боря работай


@main_router.callback_query(SettingsCallbackData.filter())
async def process_setting_callback(query: types.CallbackQuery, callback_data: SettingsCallbackData):
    reply_markup = None

    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == query.message.chat.id)).one()

        if callback_data.type == SettingType.MAILING_ENABLED:
            chat.mailing_enabled = not chat.mailing_enabled
            reply_markup = build_settings_keyboard()
            msg = get_text(
                additional_text=f'Mailing is <code>{"enabled" if chat.mailing_enabled else "disabled"}</code>.\n', chat=chat)
            session.add(chat)

        elif callback_data.type == SettingType.MAILING_TIME:
            msg = 'Choose mailing hour'
            reply_markup = build_hours_keyboard()

        elif callback_data.type == SettingType.SEND_CHURCH_HOLIDAYS:
            chat.send_church_holidays = not chat.send_church_holidays
            reply_markup = build_settings_keyboard()
            msg = get_text(
                additional_text=f'Church holidays are <code>{"enabled" if chat.send_church_holidays else "disabled"}</code>.\n', chat=chat)
            session.add(chat)

        elif callback_data.type == SettingType.SEND_COUNTRY_SPECIFIC:
            chat.send_country_specific = not chat.send_country_specific
            reply_markup = build_settings_keyboard()
            msg = get_text(
                additional_text=f'Country specific days are <code>{"enabled" if chat.send_country_specific else "disabled"}</code>.\n', chat=chat)
            session.add(chat)

        elif callback_data.type == SettingType.SEND_NAME_DAYS:
            chat.send_name_days = not chat.send_name_days
            reply_markup = build_settings_keyboard()
            msg = get_text(
                additional_text=f'Name days are <code>{"enabled" if chat.send_name_days else "disabled"}</code>.\n', chat=chat)
            session.add(chat)

        elif callback_data.type == SettingType.RESET:
            chat.mailing_enabled = False
            chat.mailing_time = 10
            chat.send_church_holidays = True
            chat.send_country_specific = True
            chat.send_name_days = True

            reply_markup = build_settings_keyboard()
            msg = get_text(
                additional_text=f'All settings reset to defaults.\n', chat=chat)
            session.add(chat)

        else:
            return

        session.commit()

    try:
        await query.message.edit_text(msg, reply_markup=reply_markup)
    except:
        await query.answer(text='Data has been updated')


@main_router.callback_query(HourCallbackData.filter())
async def process_hours_callback(query: types.CallbackQuery, callback_data: HourCallbackData):
    hour = callback_data.chosen_hour
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == query.message.chat.id)).one()
        chat.mailing_time = hour
        session.add(chat)
        session.commit()
        msg = get_text(
            additional_text=f'Mailing hours updated to <code>{chat.mailing_time}</code>.\n', chat=chat)

    reply_markup = build_settings_keyboard()

    await query.message.answer(msg, reply_markup=reply_markup)
