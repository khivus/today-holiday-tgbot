import asyncio
import logging
import json

from sqlmodel import SQLModel

from src.constants import EventFilter, dp, bot, engine, daily_json
from src.routers import main_router, admin_router
from src.models import __init__
from src.routing.admin.start_message import send_successful_start_message
from src.scheduler import scheduler


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger()
logger.addFilter(EventFilter('Failed to fetch updates'))


async def main():
    SQLModel.metadata.create_all(engine)
    
    try:
        open('daily_stats.json', 'r')
    except FileNotFoundError:
        with open('daily_stats.json', 'w') as file:
            json.dump(daily_json, file)
    
    dp.include_router(admin_router)
    dp.include_router(main_router)

    asyncio.create_task(scheduler())

    await bot.delete_webhook(drop_pending_updates=True)
    await send_successful_start_message()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
