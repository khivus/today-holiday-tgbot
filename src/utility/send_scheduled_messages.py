import datetime

from sqlmodel import Session, select
from aiogram import exceptions

from src.constants import engine, bot
from src.keyboards.page_change import build_pages_keyboard
from src.models.chat import Chat
from src.utility.chat_check import is_group_in_db
from src.utility.page_builder import build_pages
from src.utility.print_builder import better_print
from src.routing.main.page_change_action import get_holiday_message


async def send_scheluded_holidays_message():
    time_start = datetime.datetime.now()
    hour = time_start.hour
    success = 0
    with Session(engine) as session:
        chats = session.exec(select(Chat).where(Chat.mailing_time == hour).where(Chat.mailing_enabled)).all()
        for chat in chats:
            pages = await build_pages(chat_id=chat.id)
            message_text = get_holiday_message(page_index=0, pages=pages)
            keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages))
            
            try:
                await bot.send_message(chat_id=chat.id, text=message_text, reply_markup=keyboard)
                success += 1
                chat.uses += 1
                session.add(chat)
            except exceptions.TelegramForbiddenError as e:
                better_print(text=f'Chat {chat.id} will be deleted')
                session.delete(chat)
            except exceptions.TelegramMigrateToChat as e:
                better_print(text=f'{e.method}~{e.message}')
                if is_group_in_db(chat_id=e.migrate_to_chat_id, migrate_from_chat_id=chat.id) == None:
                    await bot.send_message(chat_id=e.migrate_to_chat_id, text=message_text, reply_markup=keyboard)
            except exceptions.TelegramAPIError as e:
                better_print(text=f'{e.method}~{e.message}')
                continue
            
            session.commit()
            
        time_end = datetime.datetime.now()
        time_diff = int((time_end - time_start).total_seconds() * 1000)
            
        if len(chats) != 0:
            better_print(text=f'At hour {hour}: {success} / {len(chats)} scheduled messages was send', time_diff=time_diff)
        