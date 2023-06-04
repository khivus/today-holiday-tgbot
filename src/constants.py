from aiogram import Dispatcher, Bot

from src.config import Config

config = Config()
bot = Bot(token=config.API_TOKEN, parse_mode='HTML')
dp = Dispatcher()

version = 'v0.22'
admin_id = 897276284

# TORTOISE_CONFIG = {
#     'connections': {'default': 'sqlite://resources//db.sqlite'},
#     'apps': {
#         'models': {
#             'models': ['src.models'],
#             'default_connection': 'default'
#         }
#     }
# }
