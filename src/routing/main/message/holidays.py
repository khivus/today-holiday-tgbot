import datetime

from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select
from src.models.chat import Chat
from src.models.holiday import Holiday, HolidayType

from src.routers import main_router
from src.constants import engine


@main_router.message(Command('holidays'))
async def process_holidays(message: types.Message) -> None:

    today = datetime.date.today()
    day = today.day
    month = today.month
    holidays: list[str] = []
    message_text = ['']
    index = 0

    with Session(engine) as session:
        chat = session.exec(select(Chat).where(
            Chat.id == message.chat.id)).one()
        chat.uses += 1
        session.add(chat)
        session.commit()

        results = session.exec(select(Holiday).where(
            Holiday.day == day).where(Holiday.month == month))
        for element in results:
            if (element.type == HolidayType.church and chat.send_church_holidays) \
                    or (element.type == HolidayType.country_specific and chat.send_country_specific) \
                    or (element.type == HolidayType.name_day and chat.send_name_days) \
                    or (element.type == HolidayType.normal):
                holiday = f'- {element.name}'
                if element.years_passed is not None:
                    holiday += f' - {element.years_passed}'

                holidays.append(holiday)

# TODO: сделать чанкование и пагинацию чек тг
        for string in holidays:
            if len(message_text[index]) < 4000:
                message_text[index] += '\n' + string
            else:
                message_text.append('')
                index += 1

    if len(message_text) != 0:
        for i in range(len(message_text)):
            await message.answer(text=message_text[i])
