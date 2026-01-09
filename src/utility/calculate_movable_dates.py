import datetime

from sqlmodel import Session, select

from src.constants import engine, tzinfo, Date
from src.models.holiday import Holiday

def calculate_from_easter(easter_date: datetime.date, delta_days: int = 0, delta_weeks: int = 0) -> Date:
    target_date = easter_date + datetime.timedelta(days=delta_days, weeks=delta_weeks)
    return Date(day=target_date.day, month=target_date.month)


async def calculate_movable_dates(year : int | None = None) -> None:

    movable_holidays: list = []

    if year is None:
        tnow = datetime.datetime.now(tz=tzinfo)
        year = tnow.year
    
    # Пасха (Велик день)
    # Алгоритм Меуса для юлианской Пасхи
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7

    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1

    # Дата Пасхи по юлианскому календарю
    julian_easter = datetime.date(year, month, day)

    # Разница между юлианским и григорианским календарями
    # (корректно для любого года после 1582)
    shift = year // 100 - year // 400 - 2
    easter = julian_easter + datetime.timedelta(days=shift)

    movable_holidays.append(["Пасха (Велик день)", Date(day=easter.day, month=easter.month)])
    movable_holidays.append(["Масленица", calculate_from_easter(easter_date=easter, delta_weeks=-7)])
    movable_holidays.append(["Радоница", calculate_from_easter(easter_date=easter, delta_days=9)])
    movable_holidays.append(["Троицын день (Троица)", calculate_from_easter(easter_date=easter, delta_weeks=7)])
    movable_holidays.append(["Вербная неделя (Вербное воскресенье)", calculate_from_easter(easter_date=easter, delta_weeks=-1)])
    movable_holidays.append(["Страстная неделя (Страстная пятница)", calculate_from_easter(easter_date=easter, delta_days=-2)])
    movable_holidays.append(["Светлая неделя", calculate_from_easter(easter_date=easter, delta_days=1)])
    movable_holidays.append(["Семик (Зеленые святки)", calculate_from_easter(easter_date=easter, delta_weeks=6, delta_days=4)])


    with Session(engine) as session:
        # Удаляем праздники с таким же названием
        for holiday in movable_holidays:
            results = session.exec(select(Holiday).where(Holiday.name == holiday[0]))
            
            for saved_holiday in results:
                session.delete(saved_holiday)
            
        # Записываем новые праздники с высчитанной датой
        for pending_holiday in movable_holidays:
            holiday = Holiday(name=pending_holiday[0], day=pending_holiday[1].day, month=pending_holiday[1].month)
            session.add(holiday)
            
        session.commit()
