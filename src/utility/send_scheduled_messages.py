import asyncio
import datetime
import logging as log
from collections import Counter

from sqlmodel import Session, select
from aiogram import exceptions

from src.constants import engine, bot, tzinfo
from src.keyboards.page_change import build_pages_keyboard
from src.models.chat import Chat
from src.utility.json_update import json_update
from src.utility.page_builder import build_pages, get_holiday_message


MAX_SEND_ATTEMPTS = 3


async def _send_with_retry(chat_id: int, message_text: str, keyboard) -> None:
    for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
        try:
            await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=keyboard)
            return
        except (exceptions.TelegramRetryAfter, exceptions.TelegramNetworkError,
                exceptions.TelegramServerError) as e:
            if attempt == MAX_SEND_ATTEMPTS:
                raise
            delay = e.retry_after if isinstance(e, exceptions.TelegramRetryAfter) else 2 ** (attempt - 1)
            log.warning('Scheduled send retry: chat_id=%s attempt=%s/%s delay=%ss error=%s reason=%s',
                        chat_id, attempt, MAX_SEND_ATTEMPTS, delay, type(e).__name__, e.message)
            await asyncio.sleep(delay)


async def send_scheluded_holidays_message(hour: int | None = None) -> list:
    if hour is None:
        hour = datetime.datetime.now(tz=tzinfo).hour
    success = 0
    removed = 0
    failures = Counter()

    with Session(engine) as session:
        chats = session.exec(select(Chat).where(Chat.mailing_enabled)).all()
        chat_ids = [chat.id for chat in chats
                    if (chat.mailing_time - chat.timezone) % 24 == hour]

    scheduled = len(chat_ids)
    processed_ids = set()
    for chat_id in chat_ids:
        with Session(engine) as session:
            chat = session.get(Chat, chat_id)
            if chat is None or not chat.mailing_enabled or chat_id in processed_ids:
                scheduled -= 1
                continue
            processed_ids.add(chat_id)

            try:
                # Building a message can fail too; isolate that failure to this chat.
                pages = await build_pages(chat_id=chat.id)
                message_text = get_holiday_message(page_index=0, pages=pages, chat_id=chat.id)
                keyboard = build_pages_keyboard(current_page_index=0, max_page_index=len(pages), chat_id=chat.id)

                try:
                    await _send_with_retry(chat.id, message_text, keyboard)
                except exceptions.TelegramMigrateToChat as e:
                    old_id = chat.id
                    migrated_chat = session.get(Chat, e.migrate_to_chat_id)
                    if migrated_chat is None:
                        chat.id = e.migrate_to_chat_id
                        session.add(chat)
                    else:
                        # Remove the obsolete ID even if a migration update has
                        # already created the supergroup's record.
                        if not migrated_chat.mailing_enabled:
                            migrated_chat.mailing_enabled = chat.mailing_enabled
                            migrated_chat.mailing_time = chat.mailing_time
                            migrated_chat.timezone = chat.timezone
                        migrated_chat.uses += chat.uses
                        session.delete(chat)
                        chat = migrated_chat
                    session.commit()
                    log.warning('Scheduled chat migrated: chat_id=%s new_chat_id=%s',
                                old_id, chat.id)
                    if chat.id in processed_ids:
                        scheduled -= 1
                        continue
                    processed_ids.add(chat.id)
                    await _send_with_retry(chat.id, message_text, keyboard)

                # A successful migration send must follow the same accounting path.
                success += 1
                chat.uses += 1
                session.add(chat)
                session.commit()
            except exceptions.TelegramForbiddenError as e:
                session.delete(chat)
                session.commit()
                removed += 1
                log.warning('Scheduled chat removed: chat_id=%s reason=%s', chat.id, e.message)
            except exceptions.TelegramAPIError as e:
                failures[type(e).__name__] += 1
                log.error('Scheduled send failed: chat_id=%s hour=%s error=%s reason=%s',
                          chat.id, hour, type(e).__name__, e.message)
            except Exception:
                failures['UnexpectedError'] += 1
                log.exception('Scheduled send failed: chat_id=%s hour=%s', chat_id, hour)

    json_update('succeeded_messages', success)
    json_update('all_scheduled_messages', scheduled)
    log.warning('Scheduled send summary: hour=%s succeeded=%s scheduled=%s removed=%s failures=%s',
                hour, success, scheduled, removed, dict(failures))
    return [success, scheduled]
