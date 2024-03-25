from typing import Optional

from sqlmodel import Field, SQLModel


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mailing_enabled: bool = Field(default=False, index=True)
    mailing_time: int = Field(default=8)
    uses: int = Field(default=0)
