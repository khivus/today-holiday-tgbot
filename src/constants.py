from aiogram import Dispatcher, Bot
from sqlmodel import create_engine

from src.config import Config

# TODO Don't forget to change version!
VERSION = 'v1.11.0'

# TODO Поиск праздника
# TODO Какой завтра праздник
# TODO Ежедневная стата: успешной рассылки, использований за день, новых пользователей
# TODO Сделать обход капчи

ADMIN = 897276284 # khivus' id (ADMIN ID)

config = Config()
bot = Bot(token=config.API_TOKEN, parse_mode='HTML')
dp = Dispatcher()

db_path = "resources/database.db"
engine = create_engine("sqlite:///" + db_path)
