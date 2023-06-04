from aiogram import types
from aiogram.filters import Command
from src import site_parser

# from src.models import User, Settings
from src.routers import main_router


@main_router.message(Command('start'))
async def process_start(message: types.Message) -> None:
    # user, _ = await User.get_or_create(user_id=message.from_user.id)
    # await Settings.get_or_create(user=user, defaults={})
    # user.uses += 1
    # await user.save()
    ans_text = await site_parser.parse_site()
    await message.answer(text=ans_text)
    
    # await message.answer(text='Привет! Я рассылаю снюс! Подпишись или иди нахуй)')
