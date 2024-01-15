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


class FilterCallbackData(CallbackData, prefix='Filter'):
    update: bool
    type: str


@admin_router.message(Command('filter'))
async def process_filter(message: types.Message) -> None:
    
    index = message.text.find(' ')
    if index != -1:
        temp_str = message.text[index+1:]
        split_index = temp_str.find(' ')
        
        if split_index != -1:
            holiday_type = temp_str[:split_index]
            filters = temp_str[split_index+1:]
            words: list = []
            several_index = 0
            while several_index != -1:
                several_index = filters.find(', ')
                if several_index == -1:
                    words.append(filters.strip())
                else:
                    words.append(filters[:several_index])
                filters = filters[several_index+2:]
            international_pattern = re.compile(r'in.*')
            church_pattern = re.compile(r'ch.*')
            if re.match(international_pattern, holiday_type):
                holiday_type = 'international' 
            elif re.match(church_pattern, holiday_type):
                holiday_type = 'church'
    
    builder = InlineKeyboardBuilder()
    builder.button(text='Church', callback_data=FilterCallbackData(update=False, type='church'))
    builder.button(text='International', callback_data=FilterCallbackData(update=False, type='international'))
    builder.button(text='Обновить бд', callback_data=FilterCallbackData(update=True, type=''))
    builder.adjust(2, 1)
    keyboard = builder.as_markup()
    
    if index == -1 or split_index == -1:
        message_text = 'Чтобы добавить или удалить фильтр, напиши сначала тип праздника (<code>church</code>/<code>international</code>), а после сам фильтр.\n'
        
    else:
        if not holiday_type in ['international', 'church']:
            await message.edit_text(text='Неправильно введен тип праздника!')
            return
        
        with open('filter_words.json', 'r') as file:
            filter_word = json.load(file)
        
        message_text = ''
        
        for word in words:
            if word in filter_word[f'{holiday_type}']:
                index = filter_word[f'{holiday_type}'].index(word)
                filter_word[f'{holiday_type}'].pop(index)
                message_text += f'Удален фильтр <code>{word}</code> из типа праздников <code>{holiday_type}</code>\n'
            
            else:
                filter_word[f'{holiday_type}'].append(word)
                message_text += f'Добавлен новый фильтр <code>{word}</code> в типе праздников <code>{holiday_type}</code>\n'

        with open('filter_words.json', 'w') as file:
            json.dump(filter_word, file)
    
    await message.answer(text=message_text, reply_markup=keyboard)


@admin_router.callback_query(FilterCallbackData.filter())
async def process_setting_callback(query: types.CallbackQuery, callback_data: FilterCallbackData):
    if callback_data.update:
        with open('filter_words.json', 'r') as file:
                filter_words = json.load(file)
            
        church_words = '|'.join(filter_words['church'])
        church_pattern = re.compile(rf'.*({church_words}).*',re.IGNORECASE)
        country_words = '|'.join(filter_words['international'])
        country_specific_pattern = re.compile(rf'.*({country_words}).*')

        with Session(engine) as session:
            results = session.exec(select(Holiday))

            for holiday in results:
                session.delete(holiday)
                if re.match(church_pattern, holiday.name):
                    holiday.type = HolidayType.church
                elif re.match(country_specific_pattern, holiday.name):
                    holiday.type = HolidayType.country_specific
                else:
                    holiday.type = HolidayType.normal
                session.add(holiday)
                
            session.commit()

        message_text = ['БД обновлена.']
    
    else:
        with open('filter_words.json', 'r') as file:
            filter_word = json.load(file)
        
        words = filter_word[f'{callback_data.type}']
        message_text = [f'Фильтры: ']
        index = 0
        
        for word in words:
            if word == words[0]:
                message_text[index] += f'{word}'
            if len(message_text[index]) < 4000:
                message_text[index] += f', {word}'
            else:
                index += 1
                message_text.append(f'{word}')
    
    for msgtext in message_text:
        if msgtext == message_text[0]:
            await query.message.edit_text(text=msgtext)
        else:
            await query.message.answer(text=msgtext)