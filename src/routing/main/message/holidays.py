# from datetime import datetime

from aiogram import types
from aiogram.filters import Command

# from src.models import User
from src.routers import main_router
# from src.site_parser import parse_site


@main_router.message(Command('holidays'))
async def process_holidays(message: types.Message) -> None:
    pass
    # print(datetime.now().hour, datetime.now().minute)
    # user = await User.get(user_id=message.from_user.id)
    # user.uses += 1
    # await user.save()
    # text = await parse_site()
    # await message.answer(text=text)

# TODO Today's holidays
