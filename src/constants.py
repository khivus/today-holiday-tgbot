import datetime

from aiogram import Dispatcher, Bot
from sqlmodel import create_engine

from src.config import Config

# TODO Don't forget to change version!
VERSION = 'v1.13.1'

# TODO Поиск праздника
# TODO Ридмишка

ADMIN = 897276284 # ADMIN ID

config = Config()
bot = Bot(token=config.API_TOKEN, parse_mode='HTML')
dp = Dispatcher()

db_path = "resources/database.db"
engine = create_engine("sqlite:///" + db_path)

json_template = {
    'new_chats' : 0,
    'uses' : 0,
    'succeeded_messages' : 0,
    'all_scheduled_messages' : 0
}

timezone_offset = +3.0  # GMT+3 MSK Time
tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset))