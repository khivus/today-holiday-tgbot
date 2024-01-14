import json
import re

from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from sqlmodel import Session, select

from src.models.holiday import Holiday, HolidayType
from src.routers import admin_router
from src.constants import engine


class UpdateDBCallbackData(CallbackData, prefix='UpdateDB'):
    update: bool


@admin_router.message(Command('filter_word'))
async def process_filter_word(message: types.Message) -> None:
    
    index = message.text.find(' ')
    if index != -1:
        temp_str = message.text[index+1:]
        split_index = temp_str.find(' ')
        
        if split_index != -1:
            holiday_type = temp_str[:split_index]
            word = temp_str[split_index+1:]

            international_pattern = re.compile(r'in.*')
            church_pattern = re.compile(r'ch.*')
            if re.match(international_pattern, holiday_type):
                holiday_type = 'international' 
            elif re.match(church_pattern, holiday_type):
                holiday_type = 'church'
                
    if index == -1 or split_index == -1:
        with open('filter_words.json', 'r') as file:
            filter_word = json.load(file)
        church_words = '</code>, <code>'.join(filter_word['church'])
        international_words = '</code>, <code>'.join(filter_word['international'])
        message_text = 'Чтобы добавить или удалить фильтр, напиши сначала тип праздника (<code>church</code>/<code>international</code>), а после сам фильтр.\n' \
                        f'Список церковных слов: <code>{church_words}</code>\n' \
                        f'Список национальных слов: <code>{international_words}</code>'
        keyboard = None
        
    else:
        if not holiday_type in ['international', 'church']:
            await message.edit_text(text='Неправильно введен тип праздника!')
            return
        
        with open('filter_words.json', 'r') as file:
            filter_word = json.load(file)

        if word in filter_word[f'{holiday_type}']:
            index = filter_word[f'{holiday_type}'].index(word)
            filter_word[f'{holiday_type}'].pop(index)
            message_text = f'Удален фильтр <code>{word}</code> из типа праздников <code>{holiday_type}</code>'
        
        else:
            filter_word[f'{holiday_type}'].append(word)
            message_text = f'Добавлен новый фильтр <code>{word}</code> в типе праздников <code>{holiday_type}</code>'

        with open('filter_words.json', 'w') as file:
            json.dump(filter_word, file)
        
        builder = InlineKeyboardBuilder()
        builder.button(text='Обновить бд', callback_data=UpdateDBCallbackData(update=True))
        keyboard = builder.as_markup()
    
    await message.answer(text=message_text, reply_markup=keyboard)


@admin_router.callback_query(UpdateDBCallbackData.filter())
async def process_setting_callback(query: types.CallbackQuery, callback_data: UpdateDBCallbackData):
    
    if not callback_data.update:
        await query.message.edit_reply_markup(text='Ты нажал, но не нажал на кнопку...', reply_markup=None)
        return
    
    with open('filter_words.json', 'r') as file:
            filter_words = json.load(file)
        
    church_words = '|'.join(filter_words['church'])
    church_pattern = re.compile(rf'.*({church_words}).*',re.IGNORECASE)
    country_words = '|'.join(filter_words['international'])
    country_specific_pattern = re.compile(rf'.*({country_words}).*',re.IGNORECASE)
    
    with Session(engine) as session:
        results = session.exec(select(Holiday).where(Holiday.type == HolidayType.normal))

        for holiday in results:
            session.delete(holiday)
            if re.match(country_specific_pattern, holiday.name):
                holiday.type = HolidayType.country_specific
            elif re.match(church_pattern, holiday.name):
                holiday.type = HolidayType.church
            session.add(holiday)
            
        session.commit()
    
        await query.message.edit_text(text='БД обновлена.')