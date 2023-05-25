import asyncio
import logging

from tortoise import Tortoise

from src.constants import dp, bot, TORTOISE_CONFIG
from src.routers import main_router, admin_router

logging.basicConfig(level=logging.INFO)


async def main():
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    dp.include_router(main_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())
