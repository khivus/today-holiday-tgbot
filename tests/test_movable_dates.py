"""Run with: python -m unittest discover -s tests -v."""

import asyncio
import calendar
import datetime
import importlib
import unittest
from unittest.mock import AsyncMock, patch

from sqlmodel import Session, SQLModel, create_engine, select

# Reuse the isolated application packages; never initialize the live Telegram bot.
import test_scheduled_messages as runtime

secular = importlib.import_module('src.utility.calculate_secular_dates')
movable = importlib.import_module('src.utility.calculate_movable_dates')
Holiday = importlib.import_module('src.models.holiday').Holiday
scheduler = runtime.scheduler_module


class SecularDateTests(unittest.TestCase):
    def test_dates_for_2026(self):
        expected = {
            'День матери в России': (11, 29),
            'День отца в России': (10, 18),
            'День Военно-Морского Флота России': (7, 26),
            'День железнодорожника': (8, 2),
            'День строителя': (8, 9),
            'День физкультурника в России': (8, 8),
            'День Воздушного Флота России': (8, 16),
            'День шахтера': (8, 30),
            'День танкиста': (9, 13),
            'День работников леса': (9, 20),
            'День машиностроителя': (9, 27),
            'День работника сельского хозяйства и перерабатывающей промышленности в России': (10, 11),
            'День автомобилиста (День работников автомобильного транспорта)': (10, 25),
            'День Мартина Лютера Кинга в США': (1, 19),
            'День президентов США': (2, 16),
            'День матери в США': (5, 10),
            'День памяти в США': (5, 25),
            'День отца в США': (6, 21),
            'День труда в США и Канаде': (9, 7),
            'День благодарения в США': (11, 26),
            'День благодарения в Канаде': (10, 12),
            'День работника транспорта в России': (11, 20),
        }
        actual = {name: (date.month, date.day)
                  for name, date in secular.calculate_secular_dates(2026)}
        self.assertEqual(actual, expected)

    def test_weekday_rules_against_calendar_for_a_century(self):
        for year in range(2000, 2101):
            for month in range(1, 13):
                for weekday in range(7):
                    matching_days = [day for day in range(1, calendar.monthrange(year, month)[1] + 1)
                                     if datetime.date(year, month, day).weekday() == weekday]
                    for occurrence in (1, 2, 3, 4, -1):
                        self.assertEqual(secular.weekday_in_month(year, month, weekday, occurrence).day,
                                         matching_days[occurrence - 1 if occurrence > 0 else -1])

    def test_leap_day_and_missing_fifth_occurrence(self):
        self.assertEqual(secular.weekday_in_month(2024, 2, calendar.THURSDAY, 5),
                         datetime.date(2024, 2, 29))
        self.assertEqual(secular.weekday_in_month(2024, 2, calendar.THURSDAY, -1),
                         datetime.date(2024, 2, 29))
        with self.assertRaises(ValueError):
            secular.weekday_in_month(2025, 2, calendar.THURSDAY, 5)
        for weekday, occurrence in ((7, 1), (-1, 1), (0, 0), (0, 6), (0, -2)):
            with self.subTest(weekday=weekday, occurrence=occurrence), self.assertRaises(ValueError):
                secular.weekday_in_month(2026, 2, weekday, occurrence)

    def test_catalog_is_russian_and_contains_no_religious_holidays(self):
        names = [name for name, _ in secular.calculate_secular_dates(2026)]
        self.assertEqual(len(names), len(set(names)))
        for name in names:
            self.assertNotRegex(name, '[A-Za-z]')
            self.assertNotRegex(name.lower(), 'пасх|маслениц|троиц|радониц|страстн|вербн')


class MovableDatePersistenceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        SQLModel.metadata.create_all(self.engine)
        patcher = patch.object(movable, 'engine', self.engine)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.engine.dispose)

    def saved_dates(self):
        with Session(self.engine) as session:
            holidays = session.exec(select(Holiday)).all()
            names = [holiday.name for holiday in holidays]
            self.assertEqual(len(names), len(set(names)))
            return {holiday.name: (holiday.month, holiday.day) for holiday in holidays}

    async def test_recalculation_replaces_duplicates_and_preserves_other_holidays(self):
        with Session(self.engine) as session:
            session.add_all([
                Holiday(name='День матери в России', month=11, day=1),
                Holiday(name='День матери в России', month=11, day=2),
                Holiday(name='День труда (Labor Day) в США, Канаде', month=9, day=1),
                Holiday(name='Новый год', month=1, day=1),
            ])
            session.commit()
        await movable.calculate_movable_dates(2026)
        first = self.saved_dates()
        await movable.calculate_movable_dates(2026)
        self.assertEqual(self.saved_dates(), first)
        self.assertEqual(first['Новый год'], (1, 1))
        self.assertEqual(first['Пасха (Велик день)'], (4, 12))
        self.assertNotIn('День труда (Labor Day) в США, Канаде', first)
        for name, date in secular.calculate_secular_dates(2026):
            self.assertEqual(first[name], (date.month, date.day))

        await movable.calculate_movable_dates(2027)
        second = self.saved_dates()
        self.assertEqual(set(first), set(second))
        self.assertEqual(second['День матери в России'], (11, 28))
        self.assertEqual(second['День отца в России'], (10, 17))
        self.assertEqual(second['День благодарения в США'], (11, 25))
        self.assertEqual(second['День памяти в США'], (5, 31))
        self.assertEqual(second['Пасха (Велик день)'], (5, 2))
        for name, date in secular.calculate_secular_dates(2027):
            self.assertEqual(second[name], (date.month, date.day))

    async def test_default_year_uses_bot_timezone(self):
        with patch.object(movable, 'datetime') as clock:
            clock.datetime.now.return_value.year = 2027
            clock.date.side_effect = datetime.date
            clock.timedelta.side_effect = datetime.timedelta
            await movable.calculate_movable_dates()
        clock.datetime.now.assert_called_once_with(tz=movable.tzinfo)
        self.assertEqual(self.saved_dates()['День матери в России'], (11, 28))


class AnnualRecalculationTests(unittest.IsolatedAsyncioTestCase):
    async def run_scheduler(self, times, initial_year, calculation):
        sender = AsyncMock()
        with patch.object(scheduler.datetime, 'datetime') as clock, \
                patch.object(scheduler, 'calculate_movable_dates', calculation), \
                patch.object(scheduler, 'send_scheluded_holidays_message', sender), \
                patch.object(scheduler.asyncio, 'sleep',
                             AsyncMock(side_effect=[None] * (len(times) - 1) + [asyncio.CancelledError])):
            clock.now.side_effect = times
            with self.assertRaises(asyncio.CancelledError):
                await scheduler.scheduler(calculated_year=initial_year)
        return sender

    async def test_rollover_recalculates_once_even_if_january_first_was_missed(self):
        before = datetime.datetime(2026, 12, 31, 23, 59, tzinfo=datetime.timezone.utc)
        after = datetime.datetime(2027, 1, 2, 8, 12, tzinfo=datetime.timezone.utc)
        calculation = AsyncMock()
        await self.run_scheduler([before, after, after], 2026, calculation)
        calculation.assert_awaited_once_with(year=2027)

    async def test_year_is_recalculated_before_first_mailing(self):
        now = datetime.datetime(2027, 1, 1, tzinfo=datetime.timezone.utc)
        calls = []
        async def calculate(**kwargs):
            calls.append('calculate')
        async def send(**kwargs):
            calls.append('send')
        with patch.object(scheduler.datetime, 'datetime') as clock, \
                patch.object(scheduler, 'calculate_movable_dates', calculate), \
                patch.object(scheduler, 'process_daily_stats', AsyncMock()), \
                patch.object(scheduler, 'create_db_backup', AsyncMock()), \
                patch.object(scheduler, 'send_scheluded_holidays_message', send), \
                patch.object(scheduler.asyncio, 'sleep', AsyncMock(side_effect=asyncio.CancelledError)):
            clock.now.return_value = now
            with self.assertRaises(asyncio.CancelledError):
                await scheduler.scheduler(calculated_year=2026)
        self.assertEqual(calls, ['calculate', 'send'])

    async def test_failed_calculation_is_retried(self):
        now = datetime.datetime(2027, 1, 1, 0, 2, tzinfo=datetime.timezone.utc)
        calculation = AsyncMock(side_effect=[RuntimeError('database unavailable'), None])
        with self.assertLogs(level='ERROR'):
            await self.run_scheduler([now, now, now], 2026, calculation)
        self.assertEqual([call.kwargs['year'] for call in calculation.await_args_list], [2027, 2027])

    async def test_scheduler_without_startup_year_initializes_dates(self):
        now = datetime.datetime(2026, 10, 6, 10, 2, tzinfo=datetime.timezone.utc)
        calculation = AsyncMock()
        await self.run_scheduler([now], None, calculation)
        calculation.assert_awaited_once_with(year=2026)


if __name__ == '__main__':
    unittest.main()
