from aiogram import Router, F

from src.constants import ADMINS

main_router = Router()

admin_router = Router()
for admin in ADMINS:
    admin_router.message.filter(F.from_user.id == admin)
