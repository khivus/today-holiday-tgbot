from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.keyboards.settings import build_settings_keyboard
from src.models.chat import Chat
from src.routers import main_router
from src.constants import engine


def get_text(chat: Chat, additional_text: str = ''):
    # TODO Bor
    text = f'{additional_text}' \
        f'<b>Ваши настройки</b>\n' \
        f'- Рассылка включена: <code>{chat.mailing_enabled}</code>\n' \
        f'- Время рассылки: <code>{chat.mailing_time}:00</code>\n' \
        f'- Отправлять церковные праздники: <code>{chat.send_church_holidays}</code>\n' \
        f'- Отправлять национальные праздники: <code>{chat.send_country_specific}</code>\n' \
        f'- Отправлять именины: <code>{chat.send_name_days}</code>\n' \
        '\n' \
        f'Если хотите изменить какую-то из настроек, нажмите на любую кнопку ниже.'
        # '\n' \
        # f'<b>Информация и статистика</b>\n' \
        # f'- ID пользователя: <code>{chat.id}</code>\n' \
        # f'- Использований /holiday: <code>{chat.uses}</code>\n' \

    return text


@main_router.message(Command("settings"))
async def process_settings(message: types.Message) -> None:
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == message.chat.id)).one()

    keyboard = build_settings_keyboard()

    text = get_text(chat=chat)

    await message.answer(text=text, reply_markup=keyboard)
