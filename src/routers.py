from aiogram import Router, F

from src.constants import admin_id

main_router = Router()

admin_router = Router()
admin_router.message.filter(F.from_user.id == admin_id)
