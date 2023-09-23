import asyncio
import pycron

from src.send_scheduled_messages import send_scheluded_holidays_message
from src.site_parser import parse_site


async def scheduler():
    while True:
        if pycron.is_now('0 1 * * *'):
            await parse_site()
            await asyncio.sleep(60)
        elif pycron.is_now('1 * * * *'):
            await send_scheluded_holidays_message()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)
