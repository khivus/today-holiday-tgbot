import json

from aiogram import types
from aiogram.filters import Command

from src.routers import admin_router


@admin_router.message(Command('add_banword'))
async def add_church_banword(message: types.Message) -> None:
    
    index = message.text.find(' ')
    if index != -1:
        banword = message.text[index+1:]
    
    if index == -1:
        message_text = 'Чтобы забанить слово вызови команду с нужным словом для бана через пробел.'
        
    else:
        with open('church_banwords.json', 'r') as file:
            church_banwords = json.load(file)

        church_banwords['banwords'].append(banword)

        with open('church_banwords.json', 'w') as file:
            json.dump(church_banwords, file)
        
        message_text = f'Добавлено новое слово: {banword}'
        
    await message.answer(text=message_text)
