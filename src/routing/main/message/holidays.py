import datetime

from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select
from src.models.chat import Chat
from src.models.holiday import Holiday

from src.routers import main_router
from src.constants import engine


@main_router.message(Command('holidays'))
async def process_holidays(message: types.Message) -> None:

    today = datetime.date.today()
    day = today.day
    month = today.month
    holidays: list[str] = []

    with Session(engine) as session:
        chats = session.exec(select(Chat).where(Chat.id == message.chat.id))
        for chat in chats:
            chat.uses += 1
            session.add(chat)
        session.commit()

        results = session.exec(select(Holiday).where(
            Holiday.day == day).where(Holiday.month == month))
        for element in results:
            holiday = f'- {element.name}'
            if element.years_passed is not None:
                holiday += f' - {element.years_passed}'
            holidays.append(holiday)

        message_text = '\n'.join(holidays)

    if message_text.__len__ != 0:
        await message.answer(text=message_text)
