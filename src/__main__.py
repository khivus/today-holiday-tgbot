import asyncio
import logging

from sqlmodel import SQLModel

from src.constants import dp, bot, engine
from src.routers import main_router, admin_router
from src.models import __init__
from src.scheduler import scheduler


logging.basicConfig(level=logging.INFO)


async def main():
    SQLModel.metadata.create_all(engine)

    dp.include_router(main_router)
    dp.include_router(admin_router)

    asyncio.create_task(scheduler())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
