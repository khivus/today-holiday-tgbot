import datetime
import logging

from dataclasses import dataclass
from aiogram import Dispatcher, Bot
from sqlmodel import create_engine

from src.config import Config

# TODO Don't forget to change version!
VERSION = 'v1.16.3'

# TODO Add comments to code D:
# TODO Add inline query commands /today, /tomorrow, /find (I don't want to do this :<)

ADMIN = 897276284 # ADMIN ID

config = Config()
bot = Bot(token=config.API_TOKEN, parse_mode='HTML')
dp = Dispatcher()

db_path = "resources/database.db"
engine = create_engine("sqlite:///" + db_path)

daily_json = {
    'new_chats' : 0,
    'uses' : 0,
    'succeeded_messages' : 0,
    'all_scheduled_messages' : 0
}

@dataclass
class Date():
    day: int
    month: int

class EventFilter(logging.Filter):
    def __init__(self, event_name):
        super().__init__()
        self.event_name = event_name

    def filter(self, record):
        return self.event_name in record.getMessage()

timezone_offset = +3.0  # GMT+3 MSK Time
tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))
