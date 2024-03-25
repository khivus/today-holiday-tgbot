from typing import Optional

from sqlmodel import SQLModel, Field


class Holiday(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    day: int = Field(index=True)
    month: int = Field(index=True)
