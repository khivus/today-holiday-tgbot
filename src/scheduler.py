import asyncio
import pycron

from src.routing.admin.daily_stats import process_daily_stats
from src.utility.send_scheduled_messages import send_scheluded_holidays_message
from src.utility.site_parser import parse_site


async def scheduler():
    while True:
        if pycron.is_now('1 0 * * *'):
            await process_daily_stats()
            await parse_site()
            await asyncio.sleep(60)
        elif pycron.is_now('2 * * * *'):
            await send_scheluded_holidays_message()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)
