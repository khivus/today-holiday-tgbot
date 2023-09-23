from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field


class HolidayType(str, Enum):
    normal = "normal"
    church = "church"
    country_specific = "country_specific"
    name_day = "name_day"


class Holiday(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: Optional[HolidayType] = Field(sa_column=HolidayType)
    years_passed: Optional[str] = Field(default=None)
    day: int
    month: int
