from aiogram import types
from aiogram.filters import Command

# from src.models import Settings
from src.routers import main_router
from src.routing.main.keyboard.settings import build_settings_keyboard


@main_router.message(Command('settings'))
async def process_settings(message: types.Message) -> None:
    # settings = await Settings.get(user_id=message.from_user.id)
    keyboard = build_settings_keyboard()

    await message.answer(text='List of settings to change', reply_markup=keyboard)
