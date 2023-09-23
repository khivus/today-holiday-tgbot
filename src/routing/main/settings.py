from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.keyboards.settings import build_settings_keyboard
from src.models.chat import Chat
from src.routers import main_router
from src.constants import engine


def get_text(chat: Chat, additional_text: str = ''):
    text = f'{additional_text}' \
        f'Your current settings and info:\n' \
        f'<code>Id</code> = {chat.id}\n' \
        f'<code>Mailing enabled</code> = {chat.mailing_enabled}\n' \
        f'<code>Mailing time</code> = {chat.mailing_time}\n' \
        f'<code>send_church_holidays</code> = {chat.send_church_holidays}\n' \
        f'<code>send_country_specific</code> = {chat.send_country_specific}\n' \
        f'<code>send_name_days</code> = {chat.send_name_days}\n' \
        f'<code>Uses</code> = {chat.uses}\n' \
        f'Choose setting to change.'

    return text


@main_router.message(Command("settings"))
async def process_settings(message: types.Message) -> None:
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == message.chat.id)).one()

    keyboard = build_settings_keyboard()

    text = get_text(chat=chat)

    await message.answer(text=text, reply_markup=keyboard)
