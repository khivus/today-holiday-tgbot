from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.models import Settings
from src.routers import main_router


class SettingChange(StatesGroup):
    time_state = State()


@main_router.callback_query()
async def process_settings_callback(query: types.CallbackQuery, state: FSMContext):
    settings = await Settings.get(user_id=query.from_user.id)
    if query.data == 'TIME':
        await query.message.answer(text='Введите время в формате ЧЧ:ММ')
        await state.set_state(SettingChange.time_state)


@main_router.message(SettingChange.time_state)
async def time_callback(message: types.Message, state: FSMContext):
    await state.clear()
    settings = await Settings.get(user_id=message.from_user.id)
    settings.time = message.text
    await message.answer(text='Сохранено')
    await settings.save()
