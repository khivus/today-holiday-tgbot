import asyncio

import pycron
# from tortoise import Tortoise

from src.constants import TORTOISE_CONFIG


async def main():
    # await Tortoise.init(config=TORTOISE_CONFIG)
    # await Tortoise.generate_schemas()

    pycron.start()

    # await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())
