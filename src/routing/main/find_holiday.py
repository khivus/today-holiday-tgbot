import re

from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlmodel import Session, select

from src.keyboards.cancel import CancelCallbackData, build_cancel_keyboard
from src.keyboards.days import FindDayCallbackData, build_days_keyboard
from src.keyboards.months import MonthsCallbackData, build_months_keyboard
from src.keyboards.page_change import build_pages_keyboard
from src.models.holiday import Holiday
from src.constants import Date, engine
from src.keyboards.find_holiday import FindHolidayCallbackData, FindType, build_find_holiday_keyboard
from src.routers import main_router
from src.utility.chat_check import is_group_in_db
from src.utility.new_site_parser import parse_site_page
from src.utility.page_builder import build_pages, get_holiday_message


class FindBy(StatesGroup):
    by_name = State()

@main_router.message(Command("find_holiday"))
async def process_find_holiday(message: types.Message, returned: bool | None = None) -> None:
    is_group_in_db(chat_id=message.chat.id)
    message_text = 'Выберите каким способом хотите найти праздник:'
    keyboard = build_find_holiday_keyboard()
    
    try:
        if returned:
            await message.edit_text(text=message_text, reply_markup=keyboard)
        else:
            await message.answer(text=message_text, reply_markup=keyboard)
    except:
        pass
    
@main_router.callback_query(FindHolidayCallbackData.filter())
async def process_find_holiday_callback(query: types.CallbackQuery, callback_data: FindHolidayCallbackData, state: FSMContext):
    if callback_data.find_by == FindType.BY_DATE:
        message_text = 'Выберите месяц:'
        keyboard = build_months_keyboard()
        
    elif callback_data.find_by == FindType.BY_NAME:
        message_text = 'Введите название праздника.'
        keyboard = build_cancel_keyboard()
        await state.set_state(FindBy.by_name)
        
    await query.message.edit_text(text=message_text, reply_markup=keyboard)

@main_router.callback_query(CancelCallbackData.filter())
async def process_choose_month(query: types.CallbackQuery, callback_data: CancelCallbackData, state: FSMContext) -> None:
    if callback_data.cancel:
        await state.clear()
        await process_find_holiday(message=query.message, returned=True)
        return
    
@main_router.message(FindBy.by_name)
async def process_holiday_name_input(message: types.Message, state: FSMContext) -> None:
    
    await state.clear()
    holidays: list = []
    find_pattern = re.compile(rf'.*({message.text}).*', re.IGNORECASE)
    at_least_one_found = False

    with Session(engine) as session:
        
        results = session.exec(select(Holiday))

        for holiday in results:
            if re.match(find_pattern, holiday.name):
                at_least_one_found = True
                holidays.append(f'{holiday.day:02}.{holiday.month:02} ● {holiday.name}\n')
    
    if not at_least_one_found:
        message_text: str = 'Праздников с таким именем нет.'
    elif len(holidays) > 30:
        message_text: str = 'Пожалуйста, введите более точное название.'
    else:
        message_text: str = 'Праздники с таким именем:\n' + ''.join(holidays)

    try:
        await message.answer(text=message_text)
    except:
        pass

@main_router.callback_query(MonthsCallbackData.filter())
async def process_choose_month(query: types.CallbackQuery, callback_data: MonthsCallbackData) -> None:
    
    if callback_data.chosen_month == -1:
        await process_find_holiday(message=query.message, returned=True)
        return
    
    message_text = 'Выберите день:'
    keyboard = build_days_keyboard(chosen_month=callback_data.chosen_month)
    await query.message.edit_text(text=message_text, reply_markup=keyboard)

@main_router.callback_query(FindDayCallbackData.filter())
async def process_choose_day(query: types.CallbackQuery, callback_data: FindDayCallbackData) -> None:
    
    if callback_data.chosen_day == -1:
        await process_find_holiday(message=query.message, returned=True)
        return
    
    date = Date(day=callback_data.chosen_day, month=callback_data.chosen_month)
    await parse_site_page(date=date)
    pages = await build_pages(date=date)
    message_text = get_holiday_message(page_index=0, pages=pages, date=date)
    keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages), date=date)
    
    await query.message.edit_text(text=message_text, reply_markup=keyboard)
