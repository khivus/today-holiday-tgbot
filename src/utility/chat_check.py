from sqlmodel import Session, select
from aiogram.types import Message
from datetime import datetime

from src.models.chat import Chat
from src.constants import engine
from src.routers import main_router
from src.utility.print_builder import better_print


def is_group_in_db(chat_id: int, migrate_from_chat_id: int = None) -> None:
    with Session(engine) as session:
        if not session.exec(select(Chat).where(Chat.id == chat_id)).all():
            if session.exec(select(Chat).where(Chat.id == migrate_from_chat_id)).all():
                chat = session.exec(select(Chat).where(Chat.id == migrate_from_chat_id)).one()
                chat.id = chat_id
                session.add(chat)
                session.commit()
                return None
            else:
                chat = Chat(id=chat_id)
                session.add(chat)
                session.commit()
                return False
        
        else:
            return True

def migration_filter(message: Message):
    if message.migrate_from_chat_id:
        return True

@main_router.message(migration_filter)
async def handle_update(message: Message):
    time_start = datetime.now()
    if is_group_in_db(chat_id=message.chat.id, migrate_from_chat_id=message.migrate_from_chat_id) == None:
        time_end = datetime.now()
        time_diff = int((time_end - time_start).total_seconds() * 1000)
        better_print(text=f'chat_id updated from {message.migrate_from_chat_id} to {message.chat.id}', time_diff=time_diff)