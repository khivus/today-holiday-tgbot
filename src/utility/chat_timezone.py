import datetime

from sqlmodel import Session, select
from src.constants import engine
from src.models.chat import Chat

async def get_chat_timezone(chat_id: int) -> int:
    with Session(engine) as session:
        chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
    return datetime.timezone(datetime.timedelta(hours=chat.timezone))
