import json
import re

from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router


@admin_router.message(Command('filter_word'))
async def process_filter_word(message: types.Message) -> None:
    
    index = message.text.find(' ')
    if index != -1:
        temp_str = message.text[index+1:]
        split_index = temp_str.find(' ')
        
        if split_index != -1:
            holiday_type = temp_str[:split_index]
            word = temp_str[split_index+1:]

            international_pattern = re.compile(r'int.*')
            church_pattern = re.compile(r'ch.*')
            if re.match(international_pattern, holiday_type):
                holiday_type = 'international' 
            elif re.match(church_pattern, holiday_type):
                holiday_type = 'church'
            
    if index == -1 or split_index == -1:
        with open('filter_words.json', 'r') as file:
            filter_word = json.load(file)
        church_words = ', '.join(filter_word['church'])
        international_words = ', '.join(filter_word['international'])
        message_text = 'Чтобы добавить слово фильтр, напиши сначала тип праздника (<code>church</code>/<code>international</code>), а после само слово для фильтрации.\n' \
                        f'Список церковных слов: {church_words}\n' \
                        f'Список национальных слов: {international_words}'
        
    else:
        with open('filter_words.json', 'r') as file:
            filter_word = json.load(file)

        filter_word[f'{holiday_type}'].append(word)

        with open('filter_words.json', 'w') as file:
            json.dump(filter_word, file)
        
        message_text = f'Добавлено новое фильтр слово <code>{word}</code> в тип праздников <code>{holiday_type}</code>'
        
    await message.answer(text=message_text)
