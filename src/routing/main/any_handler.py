import datetime
from aiogram import types

from src.constants import Date, tzinfo
from src.keyboards.page_change import build_pages_keyboard
from src.routers import main_router
from src.routing.main.holidays import process_holidays
from src.routing.main.tomorrow import process_tomorrow
from src.utility.chat_check import is_group_in_db
from src.utility.page_builder import build_pages, get_holiday_message


async def build_and_send(message: types.Message, date: Date | None = None) -> None:
    pages = await build_pages(date=date)
    message_text = get_holiday_message(page_index=0, pages=pages, date=date)
    keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages), date=date)
    
    try:
        await message.answer(text=message_text, reply_markup=keyboard)
    except:
        pass


@main_router.message()
async def process_any_message(message: types.Message) -> None:
    is_group_in_db(chat_id=message.chat.id)
    tnow = datetime.datetime.now(tz=tzinfo)
    weekdays: list = [
        'понедельник',
        'вторник',
        'среда',
        'четверг',
        'пятница',
        'суббота',
        'воскресенье'
    ]
    days: dict = {
        'сегодня' : 0, 
        'завтра' : 1, 
        'вчера' : -1, 
        'послезавтра' : 2, 
        'позавчера' : -2
    }

    if message.text in days:
        new_date = tnow + datetime.timedelta(days=days[message.text])
        date = Date(day=new_date.day, month=new_date.month)
        await build_and_send(message=message, date=date)

    elif message.text in weekdays:
        weekday_index = weekdays.index(message.text)
        
        weekday = tnow.weekday()

        if weekday > weekday_index:
            new_date = tnow + datetime.timedelta(days=7-(weekday-weekday_index))
        else:
            new_date = tnow + datetime.timedelta(days=weekday_index-weekday)

        date = Date(day=new_date.day, month=new_date.month)
        await build_and_send(message=message, date=date)

    elif '.' in message.text:
        try:
            raw_date: list = message.text.split('.')
            raw_date = [int(i) for i in raw_date]
            date = Date(day=raw_date[0], month=raw_date[1])
            await build_and_send(message=message, date=date)
        except:
            pass
        