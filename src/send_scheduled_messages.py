import datetime

from sqlmodel import Session, select

from src.constants import engine, bot
from src.keyboards.page_change import build_pages_keyboard
from src.models.chat import Chat
from src.page_builder import build_pages
from src.routing.main.page_change_action import get_holiday_message


async def send_scheluded_holidays_message():
    hour = datetime.datetime.now().hour
    success = 0
    with Session(engine) as session:
        chats = session.exec(select(Chat).where(
            Chat.mailing_time == hour).where(Chat.mailing_enabled)).all()
        for chat in chats:
            chat.uses += 1
            session.add(chat)

            pages = await build_pages(chat_id=chat.id)
            message_text = get_holiday_message(page_index=0, pages=pages)
            keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages))
            message = await bot.send_message(chat_id=chat.id, text=message_text, reply_markup=keyboard)
            if message:
                success += 1
        if len(chats) != 0:
            print(
                f'At hour {hour}: {success} / {len(chats)} scheduled messages was send.')
        session.commit()
