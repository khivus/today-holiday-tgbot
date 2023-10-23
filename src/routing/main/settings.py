from aiogram import types
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError
from sqlmodel import Session, select

from src.keyboards.settings import build_settings_keyboard
from src.models.chat import Chat
from src.routers import main_router
from src.constants import engine


def get_text(chat: Chat, additional_text: str = ''):
    text = f'{additional_text}' \
        '<b>Ваши настройки</b>\n' \
        f'- Рассылка включена: <code>{"Да" if chat.mailing_enabled else "Нет"}</code>\n' \
        f'- Время рассылки: <code>{chat.mailing_time}:00</code>\n' \
        f'- Отправлять церковные праздники: <code>{"Да" if chat.send_church_holidays else "Нет"}</code>\n' \
        f'- Отправлять национальные праздники: <code>{"Да" if chat.send_country_specific else "Нет"}</code>\n' \
        f'- Отправлять именины: <code>{"Да" if chat.send_name_days else "Нет"}</code>\n' \
        '\n' \
        'Если хотите изменить какую-то из настроек, нажмите на любую кнопку ниже.'

    return text


@main_router.message(Command("settings"))
async def process_settings(message: types.Message) -> None:
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == message.chat.id)).one()

        keyboard = build_settings_keyboard(chat_id=message.chat.id)
        message_text = get_text(chat=chat)
        
        try:
            await message.answer(text=message_text, reply_markup=keyboard)
        except:
            pass

        
