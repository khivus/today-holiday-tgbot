from aiogram import Dispatcher, Bot
from sqlmodel import create_engine

from src.config import Config

# TODO Don't forget to change version!
VERSION = 'v1.10.0' # Struct of version is v<major_version(release)>.<small update(new feature)>.<bug fix>

ADMIN = 897276284 # khivus' id (ADMIN ID)

config = Config()
bot = Bot(token=config.API_TOKEN, parse_mode='HTML')
dp = Dispatcher()

db_path = "resources/database.db"
engine = create_engine("sqlite:///" + db_path)
