import asyncio
import datetime

from src.routing.admin.create_db_backup import create_db_backup
from src.routing.admin.daily_stats import process_daily_stats
from src.utility.send_scheduled_messages import send_scheluded_holidays_message
from src.utility.calculate_movable_dates import calculate_movable_dates
from src.constants import tzinfo


async def scheduler():
    while True:
        tnow = datetime.datetime.now(tz=tzinfo)
        if tnow.minute == 0:
            if tnow.hour == 0:
                await process_daily_stats()
                await create_db_backup()
            await send_scheluded_holidays_message()
            await asyncio.sleep(60)
        if tnow.day == 1 and tnow.month == 1 and tnow.hour == 3 and tnow.minute == 1:
            await calculate_movable_dates()
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(1)
