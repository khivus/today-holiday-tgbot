import asyncio
import datetime
import logging as log

from src.routing.admin.create_db_backup import create_db_backup
from src.routing.admin.daily_stats import process_daily_stats
from src.utility.send_scheduled_messages import send_scheluded_holidays_message
from src.utility.calculate_movable_dates import calculate_movable_dates
from src.constants import tzinfo


async def scheduler(calculated_year: int | None = None):
    while True:
        tnow = datetime.datetime.now(tz=tzinfo)
        if calculated_year != tnow.year:
            try:
                await calculate_movable_dates(year=tnow.year)
            except Exception:
                log.exception('Scheduled holiday date calculation failed')
            else:
                calculated_year = tnow.year

        if tnow.minute == 0:
            if tnow.hour == 0:
                for task in (process_daily_stats, create_db_backup):
                    try:
                        await task()
                    except Exception:
                        log.exception('Scheduled admin task failed: %s', task.__name__)
            try:
                await send_scheluded_holidays_message(hour=tnow.hour)
            except Exception:
                log.exception('Scheduled mailing batch failed: hour=%s', tnow.hour)
            await asyncio.sleep(60)
        await asyncio.sleep(1)
