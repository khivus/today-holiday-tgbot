import asyncio
import aioschedule

from src.scheduled_holidays import send_scheluded_holidays_message
from src.site_parser import parse_site


async def scheduler():
    aioschedule.every().day.at("00:00").do(parse_site)
    aioschedule.every().hour.at(":01").do(send_scheluded_holidays_message)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

# TODO scheduler to work
