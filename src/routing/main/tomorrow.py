import datetime

from aiogram import types
from aiogram.filters import Command
from sqlmodel import Session, select

from src.keyboards.page_change import build_pages_keyboard
from src.models.chat import Chat
from src.models.holiday import Holiday
from src.utility.chat_check import is_group_in_db
from src.utility.json_update import json_update
from src.utility.page_builder import build_pages
from src.routers import main_router
from src.constants import engine, tzinfo, Date
from src.routing.main.page_change_action import get_holiday_message
from src.utility.site_parser import parse_site
        

@main_router.message(Command('tomorrow'))
async def process_tomorrow(message: types.Message) -> None:
    is_group_in_db(chat_id=message.chat.id)
    
    tnow = datetime.datetime.now(tz=tzinfo)
    tomorrow = tnow + datetime.timedelta(days=1)
    date = Date(day=tomorrow.day, month=tomorrow.month)
    
    with Session(engine) as session:
        selected = select(Holiday).where(Holiday.day == date.day).where(Holiday.month == date.month)
        results = session.exec(selected)
        
        if not results.all():
            await parse_site(url='https://calend.online/holiday/tomorrow/', date=date)
                
        results = session.exec(selected)
        chat = session.exec(select(Chat).where(Chat.id == message.chat.id)).one()
        
        pages = await build_pages(chat_id=message.chat.id, date=date)
        message_text = get_holiday_message(page_index=0, pages=pages, date=date)
        keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages), date=date)

        try:
            await message.answer(text=message_text, reply_markup=keyboard)
        except:
            pass
        
        chat.uses += 1
        session.add(chat)
        session.commit()
        json_update('uses')
    