from typing import Optional

from sqlmodel import Field, SQLModel


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mailing_enabled: bool = Field(default=False)
    mailing_time: int = Field(default=8)
    send_church_holidays: bool = Field(default=True)
    send_country_specific: bool = Field(default=True)
    send_name_days: bool = Field(default=True)
    uses: int = Field(default=0)
