"""Правила расчёта популярных светских праздников."""

import calendar
import datetime


def weekday_in_month(year: int, month: int, weekday: int, occurrence: int) -> datetime.date:
    """Дата N-го дня недели в месяце; -1 означает последний день недели."""
    if weekday not in range(7):
        raise ValueError('День недели должен быть от 0 до 6')
    if occurrence not in (-1, 1, 2, 3, 4, 5):
        raise ValueError('Номер недели должен быть от 1 до 5 или -1')

    first_weekday, days_in_month = calendar.monthrange(year, month)
    if occurrence == -1:
        last_weekday = datetime.date(year, month, days_in_month).weekday()
        day = days_in_month - (last_weekday - weekday) % 7
    else:
        day = 1 + (weekday - first_weekday) % 7 + 7 * (occurrence - 1)
        if day > days_in_month:
            raise ValueError('В этом месяце нет указанного дня недели')
    return datetime.date(year, month, day)


# Название, месяц, день недели, порядковый номер (-1 — последний).
# Названия существующих записей сохранены, чтобы заменить устаревшие даты.
SECULAR_HOLIDAY_RULES = (
    ('День матери в России', 11, calendar.SUNDAY, -1),
    ('День отца в России', 10, calendar.SUNDAY, 3),
    ('День Военно-Морского Флота России', 7, calendar.SUNDAY, -1),
    ('День железнодорожника', 8, calendar.SUNDAY, 1),
    ('День строителя', 8, calendar.SUNDAY, 2),
    ('День физкультурника в России', 8, calendar.SATURDAY, 2),
    ('День Воздушного Флота России', 8, calendar.SUNDAY, 3),
    ('День шахтера', 8, calendar.SUNDAY, -1),
    ('День танкиста', 9, calendar.SUNDAY, 2),
    ('День работников леса', 9, calendar.SUNDAY, 3),
    ('День машиностроителя', 9, calendar.SUNDAY, -1),
    ('День работника сельского хозяйства и перерабатывающей промышленности в России',
     10, calendar.SUNDAY, 2),
    ('День автомобилиста (День работников автомобильного транспорта)',
     10, calendar.SUNDAY, -1),
    ('День Мартина Лютера Кинга в США', 1, calendar.MONDAY, 3),
    ('День президентов США', 2, calendar.MONDAY, 3),
    ('День матери в США', 5, calendar.SUNDAY, 2),
    ('День памяти в США', 5, calendar.MONDAY, -1),
    ('День отца в США', 6, calendar.SUNDAY, 3),
    ('День труда в США и Канаде', 9, calendar.MONDAY, 1),
    ('День благодарения в США', 11, calendar.THURSDAY, 4),
    ('День благодарения в Канаде', 10, calendar.MONDAY, 2),
)

# Прежнее название из парсера содержит английский текст.
SECULAR_HOLIDAY_ALIASES = ('День труда (Labor Day) в США, Канаде',)


def calculate_secular_dates(year: int) -> list[tuple[str, datetime.date]]:
    holidays = [
        (name, weekday_in_month(year, month, weekday, occurrence))
        for name, month, weekday, occurrence in SECULAR_HOLIDAY_RULES
    ]
    # Общий День работника транспорта имеет фиксированную дату — 20 ноября.
    holidays.append(('День работника транспорта в России', datetime.date(year, 11, 20)))
    return holidays
