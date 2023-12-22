import asyncio
import datetime

from src.routing.admin.create_db_backup import create_db_backup
from src.routing.admin.daily_stats import process_daily_stats
from src.utility.send_scheduled_messages import send_scheluded_holidays_message
from src.utility.site_parser import parse_site
from src.constants import tzinfo


async def scheduler():
    while True:
        tnow = datetime.datetime.now(tz=tzinfo)
        if tnow.minute == 1:
            if tnow.hour == 0:
                await process_daily_stats()
                await create_db_backup()
                await parse_site()
            await send_scheluded_holidays_message()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)
