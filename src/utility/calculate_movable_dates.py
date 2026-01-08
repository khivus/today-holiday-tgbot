import asyncio
import datetime

from sqlmodel import Session, select

from src.constants import engine, tzinfo, Date
from src.models.holiday import Holiday


# https://ru.wikipedia.org/wiki/%D0%9F%D0%B5%D1%80%D0%B5%D1%85%D0%BE%D0%B4%D1%8F%D1%89%D0%B8%D0%B5_%D0%BF%D1%80%D0%B0%D0%B7%D0%B4%D0%BD%D0%B8%D0%BA%D0%B8#%D0%A1%D0%BB%D0%B0%D0%B2%D1%8F%D0%BD%D1%81%D0%BA%D0%B8%D0%B5_%D1%82%D1%80%D0%B0%D0%B4%D0%B8%D1%86%D0%B8%D0%B8
async def calculate_movable_dates() -> None:

    movable_holidays: list = []

    tnow = datetime.datetime.now(tz=tzinfo)
    year = tnow.year
    
    # Пасха
    holiday_name = "Пасха"

    a_mod19 = year % 19
    c = (a_mod19 * 19 + 15) % 30
    b = year % 4
    cc = year % 7
    d = (2 * b + 4 * c + 6 * cc + 6) % 7
    total = 4 + c + d
    if total > 30:
        day = total - 30
        month = 5
    else:
        day = total
        month = 4

    movable_holidays.append({"name" : holiday_name, 
                             "day" : day, 
                             "month" : month})




    print("Calculated holidays:")
    for holiday in movable_holidays:
        print(f"{holiday["name"]}: {holiday["day"]}.{holiday["month"]}")

    # with Session(engine) as session:
    #     # Удаляем праздники с таким же названием
    #     for holiday in movable_holidays:
    #         results = session.exec(select(Holiday).where(Holiday.name == holiday["name"]))
            
    #         for saved_holiday in results:
    #             session.delete(saved_holiday)
            
    #     # Записываем новые праздники с высчитанной датой
    #     for pending_holiday in movable_holidays:
    #         holiday = Holiday(name=pending_holiday[0], day=date.day, month=date.month)
    #         session.add(holiday)
            
    #     session.commit()

