import datetime

from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.keyboards.page_change import build_pages_keyboard
from src.models.chat import Chat
from src.models.holiday import Holiday, HolidayType
from src.routers import main_router
from src.constants import engine


def build_pages(message: types.Message):

    today = datetime.date.today()
    day = today.day
    month = today.month
    pages = ['']
    old_index = 0
    index = 0
    skip = False

    with Session(engine) as session:
        results = session.exec(select(Holiday).where(
            Holiday.day == day).where(Holiday.month == month))
        chat = session.exec(select(Chat).where(
            Chat.id == message.chat.id)).one()

        for element in results:
            holiday_text = f'- {element.name}'
            if element.years_passed is not None:
                holiday_text += f' - {element.years_passed}'

            if element.type == HolidayType.normal:
                new_index = 0
            elif element.type == HolidayType.church and chat.send_church_holidays:
                new_index = 1
            elif element.type == HolidayType.country_specific and chat.send_country_specific:
                new_index = 2
            elif element.type == HolidayType.name_day and chat.send_name_days:
                new_index = 3
            else:
                skip = True

            if not skip:
                if old_index != new_index:
                    pages.append('')
                    index += 1
                    old_index = new_index

                pages[index] += holiday_text + '\n'
            skip = False

    return pages


@main_router.message(Command('holidays'))
async def process_holidays(message: types.Message) -> None:

    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == message.chat.id)).one()
        chat.uses += 1
        session.add(chat)
        session.commit()

    pages = build_pages(message=message)
    keyboard = build_pages_keyboard(current_page_index=0)

    if len(pages[0]) != 0:
        await message.answer(text=pages[0], reply_markup=keyboard)
