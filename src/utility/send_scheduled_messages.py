import datetime
import traceback
import logging as log

from sqlmodel import Session, select
from aiogram import exceptions

from src.constants import engine, bot, tzinfo
from src.keyboards.page_change import build_pages_keyboard
from src.models.chat import Chat
from src.utility.chat_check import is_group_in_db
from src.utility.json_update import json_update
from src.utility.page_builder import build_pages, get_holiday_message


async def send_scheluded_holidays_message(hour: int | None = None) -> list:
    
    if hour == None:
        tnow = datetime.datetime.now(tz=tzinfo)
        hour = tnow.hour
    success = 0
    
    with Session(engine) as session:
        chats = session.exec(select(Chat).where(Chat.mailing_time == hour).where(Chat.mailing_enabled)).all()
        for chat in chats:
            pages = await build_pages()
            message_text = get_holiday_message(page_index=0, pages=pages)
            keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages))
            
            try:
                await bot.send_message(chat_id=chat.id, text=message_text, reply_markup=keyboard)
                success += 1
                chat.uses += 1
                session.add(chat)
            except exceptions.TelegramForbiddenError as e:
                session.delete(chat)
                print(f'Chat {chat.id} is deleted')
            except exceptions.TelegramMigrateToChat as e:
                log.error(f'{e.method}: {e.message}')
                if is_group_in_db(chat_id=e.migrate_to_chat_id, migrate_from_chat_id=chat.id) == None:
                    await bot.send_message(chat_id=e.migrate_to_chat_id, text=message_text, reply_markup=keyboard)
            except exceptions.TelegramAPIError as e:
                log.error(f'{e.method}: {e.message}')
                continue
            except Exception as e:
                # chat.mailing_enabled = False
                # session.add(chat)
                error_type = type(e).__name__
                log.error(f'Error happened in chat {chat.id}: {error_type} - {e}')
                log.error(traceback.format_exc())
                # log.error(f'Unknown error happened, mailing for chat {chat.id} disabled.')
                continue
            
            session.commit()
    
    json_update('succeeded_messages', success)
    json_update('all_scheduled_messages', len(chats))

    return [success, len(chats)]