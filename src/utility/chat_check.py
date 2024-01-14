from sqlmodel import Session, select
from aiogram.types import Message

from src.models.chat import Chat
from src.constants import engine
from src.routers import main_router


def is_group_in_db(chat_id: int, migrate_from_chat_id: int | None = None) -> bool | None:
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

def migration_filter(message: Message) -> None:
    if message.migrate_from_chat_id:
        return True

@main_router.message(migration_filter)
async def handle_update(message: Message) -> None:
    if is_group_in_db(chat_id=message.chat.id, migrate_from_chat_id=message.migrate_from_chat_id) == None:
        print(f'chat_id updated from {message.migrate_from_chat_id} to {message.chat.id}')