from sqlmodel import Session, select

from src.models.chat import Chat
from src.constants import engine

def chat_check(chat_id: int, migrate_from_chat_id: int = None, migrate_to_chat_id: int = None) -> None:
    with Session(engine) as session:
        if not session.exec(select(Chat).where(Chat.id == chat_id)).one():
            if migrate_to_chat_id and migrate_from_chat_id:
                if session.exec(select(Chat).where(Chat.id == migrate_from_chat_id)).one():
                    chat = session.exec(select(Chat).where(Chat.id == migrate_from_chat_id)).one()
                    chat.id = migrate_to_chat_id
            else:
                chat = Chat(id=chat_id)
            session.add(chat)
            session.commit()
            return False
        
        else:
            return True