"""Run with: python -m unittest discover -s tests -v.

Load only the modules under test: importing src normally initializes the live bot.
All Telegram calls are simulated and databases are temporary/in memory.
"""
import asyncio
import datetime
import importlib.util
import logging
import sys
import types
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import AsyncMock, patch

from aiogram import Dispatcher, exceptions
from aiogram.methods import GetUpdates, SendMessage
from aiogram.types import Update
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
polling_logging = load_module('src.utility.polling_logging', 'src/utility/polling_logging.py')
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
        self.bot.send_message.side_effect = self.error(exceptions.TelegramBadRequest, message='Bad Request: message is too long')
        with self.assertLogs(level='ERROR') as logs:
            self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [0, 1])
        self.assertIn('reason=Bad Request: message is too long', '\n'.join(logs.output))
        self.assertIsNotNone(self.get_chat(1))
        self.assertTrue(self.get_chat(1).mailing_enabled)
        self.assertEqual(self.bot.send_message.await_count, 1)

    async def test_chat_not_found_is_removed_and_batch_continues(self):
        for reason in ('chat not found', 'Bad Request: chat not found'):
            with self.subTest(reason=reason):
                self.add_chat()
                self.add_chat(2)
                self.bot.send_message.reset_mock()
                self.bot.send_message.side_effect = [
                    self.error(exceptions.TelegramBadRequest, message=reason), None]
                with self.assertLogs(level='WARNING') as logs:
                    self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 2])
                self.assertIsNone(self.get_chat(1))
                self.assertEqual(self.get_chat(2).uses, 1)
                self.assertEqual(self.bot.send_message.await_count, 2)
                self.assertIn('removed=1 disabled=0 failures={}', '\n'.join(logs.output))
                self.bot.send_message.side_effect = None
                self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
                with Session(self.engine) as session:
                    session.delete(session.get(Chat, 2))
                    session.commit()

    async def test_closed_topic_pauses_mailing_and_preserves_settings(self):
        self.add_chat(uses=7)
        self.add_chat(2)
        self.bot.send_message.side_effect = [
            self.error(exceptions.TelegramBadRequest, message='Bad Request: TOPIC_CLOSED'), None]
        with self.assertLogs(level='WARNING') as logs:
            self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 2])
        chat = self.get_chat(1)
        self.assertFalse(chat.mailing_enabled)
        self.assertEqual((chat.uses, chat.mailing_time, chat.timezone), (7, 8, 3))
        self.assertEqual(self.stats['succeeded_messages'], 1)
        self.assertEqual(self.stats['all_scheduled_messages'], 2)
        self.assertIn('removed=0 disabled=1 failures={}', '\n'.join(logs.output))
        self.bot.send_message.side_effect = None
        self.bot.send_message.reset_mock()
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        self.assertEqual(self.bot.send_message.call_args.kwargs['chat_id'], 2)
        with Session(self.engine) as session:
            chat = session.get(Chat, 1)
            chat.mailing_enabled = True
            session.add(chat)
            session.commit()
        self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [2, 2])
        self.assertEqual(self.get_chat(1).uses, 8)

    async def test_bad_requests_after_migration_use_new_chat(self):
        for reason, removed in (('Bad Request: chat not found', True), ('Bad Request: TOPIC_CLOSED', False)):
            with self.subTest(reason=reason):
                self.add_chat()
                self.bot.send_message.side_effect = [
                    self.error(exceptions.TelegramMigrateToChat, migrate_to_chat_id=-1001),
                    self.error(exceptions.TelegramBadRequest, chat_id=-1001, message=reason)]
                with self.assertLogs(level='WARNING') as logs:
                    self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [0, 1])
                self.assertIsNone(self.get_chat(1))
                self.assertIn('chat_id=-1001 reason=', '\n'.join(logs.output))
                migrated = self.get_chat(-1001)
                if removed:
                    self.assertIsNone(migrated)
                else:
                    self.assertFalse(migrated.mailing_enabled)

    async def test_successful_summary_is_info(self):
        self.add_chat()
        with self.assertLogs(level='INFO') as logs:
            self.assertEqual(await sender.send_scheluded_holidays_message(hour=5), [1, 1])
        self.assertEqual([record.levelno for record in logs.records], [logging.INFO])

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


class PollingLoggingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.logger = logging.getLogger('aiogram.dispatcher')
        self.addCleanup(self.logger.setLevel, self.logger.level)
        self.addCleanup(setattr, self.logger, 'filters', self.logger.filters[:])
        polling_logging.configure_polling_logging()

    async def test_network_errors_retry_and_recover_without_error_logs(self):
        bot = AsyncMock()
        bot.id = 123
        bot.session.timeout = 60
        method = GetUpdates()
        bot.side_effect = [
            exceptions.TelegramNetworkError(method=method, message='ServerDisconnectedError: Server disconnected'),
            exceptions.TelegramNetworkError(method=method, message='ClientConnectorError: Temporary failure in name resolution'),
            [Update(update_id=42)]]
        updates = Dispatcher._listen_updates(bot)
        try:
            with patch('aiogram.utils.backoff.Backoff.asleep', new_callable=AsyncMock) as sleep, \
                    self.assertLogs('aiogram.dispatcher', level='INFO') as logs:
                self.assertEqual((await anext(updates)).update_id, 42)
            self.assertEqual(bot.await_count, 3)
            self.assertEqual(sleep.await_count, 2)
            self.assertFalse(any(record.levelno >= logging.ERROR for record in logs.records))
            self.assertIn('ServerDisconnectedError', '\n'.join(logs.output))
            self.assertIn('Temporary failure in name resolution', '\n'.join(logs.output))
            self.assertIn('Connection established', '\n'.join(logs.output))
        finally:
            await updates.aclose()

    async def test_server_error_is_warning_but_conflict_remains_error(self):
        method = GetUpdates()
        for kind, level in ((exceptions.TelegramServerError, logging.WARNING),
                            (exceptions.TelegramConflictError, logging.ERROR)):
            with self.subTest(kind=kind), self.assertLogs('aiogram.dispatcher', level='INFO') as logs:
                error = kind(method=method, message='test failure')
                self.logger.error('Failed to fetch updates - %s: %s', type(error).__name__, error)
            self.assertEqual(logs.records[0].levelno, level)

    async def test_unrelated_dispatcher_error_keeps_severity(self):
        error = exceptions.TelegramNetworkError(method=GetUpdates(), message='offline')
        with self.assertLogs('aiogram.dispatcher', level='INFO') as logs:
            self.logger.error('Unrelated error: %s', error)
        self.assertEqual(logs.records[0].levelno, logging.ERROR)

    async def test_configuration_keeps_recovery_visible_and_is_idempotent(self):
        polling_logging.configure_polling_logging()
        self.assertEqual(self.logger.level, logging.INFO)
        self.assertEqual(sum(isinstance(item, polling_logging.TransientPollingErrorFilter)
                             for item in self.logger.filters), 1)


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
                await scheduler_module.scheduler(calculated_year=now.year)
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
                await scheduler_module.scheduler(calculated_year=now.year)
        self.assertEqual([call.kwargs['hour'] for call in send.await_args_list], [5, 6])


if __name__ == '__main__':
    unittest.main()
