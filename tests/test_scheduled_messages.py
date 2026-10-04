"""Run with: python -m unittest discover -s tests -v.

Load only the modules under test: importing src normally initializes the live bot.
All Telegram calls are simulated and databases are temporary/in memory.
"""
import asyncio
import datetime
import importlib.util
import sys
import types
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import AsyncMock, patch

from aiogram import exceptions
from aiogram.methods import SendMessage
from sqlmodel import Session, SQLModel, create_engine


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Bypass application package initializers and credentials for isolated testing.
for name, directory in [('src', 'src'), ('src.models', 'src/models'),
                        ('src.utility', 'src/utility'), ('src.keyboards', 'src/keyboards'),
                        ('src.routing', 'src/routing'), ('src.routing.admin', 'src/routing/admin')]:
    package = types.ModuleType(name)
    package.__path__ = [str(ROOT / directory)]
    sys.modules[name] = package

constants = types.ModuleType('src.constants')
constants.engine = create_engine('sqlite://')
constants.bot = types.SimpleNamespace(send_message=AsyncMock())
constants.tzinfo = datetime.timezone.utc
constants.Date = types.SimpleNamespace
sys.modules['src.constants'] = constants

chat_module = load_module('src.models.chat', 'src/models/chat.py')
load_module('src.models.holiday', 'src/models/holiday.py')
sender = load_module('src.utility.send_scheduled_messages', 'src/utility/send_scheduled_messages.py')
Chat = chat_module.Chat

for name in ('daily_stats', 'create_db_backup'):
    stub = types.ModuleType(f'src.routing.admin.{name}')
    setattr(stub, 'process_daily_stats' if name == 'daily_stats' else name, AsyncMock())
    sys.modules[stub.__name__] = stub
scheduler_module = load_module('src.scheduler', 'src/scheduler.py')


class ScheduledMessagesTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        SQLModel.metadata.create_all(self.engine)
        self.bot = types.SimpleNamespace(send_message=AsyncMock())
        self.stats = Counter()
        self.sleep = AsyncMock()
        for module in (sender, sys.modules['src.utility.page_builder'],
                       sys.modules['src.utility.chat_timezone']):
            patcher = patch.object(module, 'engine', self.engine)
            patcher.start()
            self.addCleanup(patcher.stop)
        for patcher in (patch.object(sender, 'bot', self.bot),
                        patch.object(sender, 'json_update', self.update_stats),
                        patch.object(sender.asyncio, 'sleep', self.sleep)):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.engine.dispose)

    def update_stats(self, key, value):
        self.stats[key] += value

    def add_chat(self, chat_id=1, **values):
        values.setdefault('mailing_enabled', True)
        with Session(self.engine) as session:
            session.add(Chat(id=chat_id, **values))
            session.commit()

    def error(self, kind, chat_id=1, message='test failure', **values):
        return kind(method=SendMessage(chat_id=chat_id, text='test'), message=message, **values)

    def get_chat(self, chat_id):
        with Session(self.engine) as session:
            return session.get(Chat, chat_id)

    async def test_midnight_is_not_replaced_by_current_hour(self):
        self.add_chat(mailing_time=3, timezone=3)
        self.add_chat(2, mailing_time=4, timezone=3)
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=0), [1, 1])
        self.assertEqual(self.bot.send_message.call_args.kwargs['chat_id'], 1)
        self.assertEqual(self.get_chat(1).uses, 1)
        self.assertEqual(self.stats['succeeded_messages'], 1)
        self.assertEqual(self.stats['all_scheduled_messages'], 1)

    async def test_default_hour_uses_utc(self):
        self.add_chat(mailing_time=8, timezone=3)
        with patch.object(sender, 'datetime') as clock:
            clock.datetime.now.return_value.hour = 5
            self.assertEqual(await sender.send_scheluded_holidays_message(), [1, 1])
            clock.datetime.now.assert_called_once_with(tz=datetime.timezone.utc)

    async def test_timezone_wraps_to_previous_utc_day(self):
        self.add_chat(mailing_time=1, timezone=3)
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=22), [1, 1])

    async def test_rate_limit_waits_then_counts_one_success(self):
        self.add_chat()
        self.bot.send_message.side_effect = [
            self.error(exceptions.TelegramRetryAfter, retry_after=7), None]
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        self.sleep.assert_awaited_once_with(7)
        self.assertEqual(self.get_chat(1).uses, 1)

    async def test_network_and_server_errors_retry(self):
        self.add_chat()
        self.bot.send_message.side_effect = [self.error(exceptions.TelegramNetworkError),
                                             self.error(exceptions.TelegramServerError), None]
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        self.assertEqual([call.args[0] for call in self.sleep.await_args_list], [1, 2])

    async def test_retry_exhaustion_logs_chat_and_continues(self):
        self.add_chat()
        self.add_chat(2)
        self.bot.send_message.side_effect = [self.error(exceptions.TelegramNetworkError)] * 3 + [None]
        with self.assertLogs(level='ERROR') as logs:
            self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 2])
        self.assertIn('chat_id=1', '\n'.join(logs.output))
        self.assertIn('TelegramNetworkError', '\n'.join(logs.output))
        self.assertIsNotNone(self.get_chat(1))
        self.assertEqual(self.get_chat(2).uses, 1)

    async def test_bad_request_is_retained_and_reason_is_logged(self):
        self.add_chat()
        self.bot.send_message.side_effect = self.error(exceptions.TelegramBadRequest, message='chat not found')
        with self.assertLogs(level='ERROR') as logs:
            self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [0, 1])
        self.assertIn('reason=chat not found', '\n'.join(logs.output))
        self.assertIsNotNone(self.get_chat(1))
        self.assertEqual(self.bot.send_message.await_count, 1)

    async def test_forbidden_chat_is_deleted_and_not_scheduled_again(self):
        self.add_chat()
        self.bot.send_message.side_effect = self.error(exceptions.TelegramForbiddenError)
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [0, 1])
        self.assertIsNone(self.get_chat(1))
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [0, 0])

    async def test_message_build_failure_does_not_stop_remaining_chats(self):
        self.add_chat()
        self.add_chat(2)
        with patch.object(sender, 'build_pages', AsyncMock(side_effect=[ValueError('invalid data'), ['holiday']])):
            with self.assertLogs(level='ERROR'):
                self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 2])
        self.assertEqual(self.bot.send_message.call_args.kwargs['chat_id'], 2)

    async def test_migration_preserves_subscription_and_counts_success(self):
        self.add_chat(uses=8)
        self.bot.send_message.side_effect = [self.error(exceptions.TelegramMigrateToChat,
                                                       migrate_to_chat_id=-1001), None]
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        self.assertIsNone(self.get_chat(1))
        migrated = self.get_chat(-1001)
        self.assertEqual(migrated.uses, 9)
        self.assertTrue(migrated.mailing_enabled)
        self.assertEqual(self.bot.send_message.call_args.kwargs['chat_id'], -1001)

    async def test_migration_second_send_errors_are_handled(self):
        self.add_chat()
        self.add_chat(2)
        self.bot.send_message.side_effect = [self.error(exceptions.TelegramMigrateToChat,
                                                       migrate_to_chat_id=-1001),
                                             self.error(exceptions.TelegramForbiddenError, chat_id=-1001), None]
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 2])
        self.assertIsNone(self.get_chat(-1001))
        self.assertEqual(self.get_chat(2).uses, 1)

    async def test_migration_to_existing_chat_does_not_send_twice(self):
        self.add_chat(-10)
        self.add_chat(-1, uses=3)
        self.bot.send_message.side_effect = [self.error(exceptions.TelegramMigrateToChat,
                                                       chat_id=-10, migrate_to_chat_id=-1), None]
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        self.assertIsNone(self.get_chat(-10))
        self.assertEqual(self.get_chat(-1).uses, 4)
        self.assertEqual(self.bot.send_message.await_count, 2)

    async def test_migration_to_existing_disabled_chat_keeps_subscription(self):
        self.add_chat(-10, uses=2)
        self.add_chat(-1, mailing_enabled=False, mailing_time=11, timezone=1, uses=3)
        self.bot.send_message.side_effect = [self.error(exceptions.TelegramMigrateToChat,
                                                       chat_id=-10, migrate_to_chat_id=-1), None]
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        migrated = self.get_chat(-1)
        self.assertTrue(migrated.mailing_enabled)
        self.assertEqual((migrated.mailing_time, migrated.timezone, migrated.uses), (8, 3, 6))


class SchedulerTests(unittest.IsolatedAsyncioTestCase):
    async def test_admin_failures_do_not_stop_midnight_mailing(self):
        now = datetime.datetime(2026, 10, 4, 0, 0, tzinfo=datetime.timezone.utc)
        stats = AsyncMock(side_effect=exceptions.TelegramNetworkError(
            method=SendMessage(chat_id=1, text='stats'), message='offline'))
        stats.__name__ = 'process_daily_stats'
        backup = AsyncMock(side_effect=RuntimeError('backup failed'))
        backup.__name__ = 'create_db_backup'
        send = AsyncMock()
        with patch.object(scheduler_module.datetime, 'datetime') as clock, \
                patch.object(scheduler_module, 'process_daily_stats', stats), \
                patch.object(scheduler_module, 'create_db_backup', backup), \
                patch.object(scheduler_module, 'send_scheluded_holidays_message', send), \
                patch.object(scheduler_module.asyncio, 'sleep', AsyncMock(side_effect=asyncio.CancelledError)), \
                self.assertLogs(level='ERROR'):
            clock.now.return_value = now
            with self.assertRaises(asyncio.CancelledError):
                await scheduler_module.scheduler()
        send.assert_awaited_once_with(hour=0)
        backup.assert_awaited_once()

    async def test_batch_failure_does_not_kill_scheduler(self):
        now = datetime.datetime(2026, 10, 4, 5, 0, tzinfo=datetime.timezone.utc)
        send = AsyncMock(side_effect=[RuntimeError('broken batch'), None])
        with patch.object(scheduler_module.datetime, 'datetime') as clock, \
                patch.object(scheduler_module, 'send_scheluded_holidays_message', send), \
                patch.object(scheduler_module.asyncio, 'sleep', AsyncMock(side_effect=[None, None, asyncio.CancelledError])), \
                self.assertLogs(level='ERROR'):
            clock.now.side_effect = [now, now.replace(hour=6)]
            with self.assertRaises(asyncio.CancelledError):
                await scheduler_module.scheduler()
        self.assertEqual([call.kwargs['hour'] for call in send.await_args_list], [5, 6])


if __name__ == '__main__':
    unittest.main()
