import asyncio
import datetime

from src.routing.admin.create_db_backup import create_db_backup
from src.routing.admin.daily_stats import process_daily_stats
from src.utility.new_site_parser import parse_all_site_pages, parse_site_page
from src.utility.send_scheduled_messages import send_scheluded_holidays_message
from src.constants import tzinfo


async def scheduler():
    while True:
        tnow = datetime.datetime.now(tz=tzinfo)
        if tnow.minute == 1:
            if tnow.hour == 0:
                await process_daily_stats()
                await create_db_backup()
                await parse_site_page()
            await send_scheluded_holidays_message()
            await asyncio.sleep(60)
        if tnow.day == 1 and tnow.month == 1 and tnow.hour == 6 and tnow.minute == 1:
            await parse_all_site_pages()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)
