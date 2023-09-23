from aiogram import Dispatcher, Bot
from sqlmodel import create_engine

from src.config import Config

# TODO Don't forget to change version!
version = 'v0.31'

ADMIN = 897276284

# ADMINS = (
#     897276284,  # khivus
#     448565207   # boryaxta
# )

config = Config()
bot = Bot(token=config.API_TOKEN, parse_mode='HTML')
dp = Dispatcher()

db_path = "resources/database.db"
engine = create_engine("sqlite:///" + db_path)
