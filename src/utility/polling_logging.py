import logging

from aiogram import exceptions


class TransientPollingErrorFilter(logging.Filter):
    """Keep aiogram's polling retries visible at their expected severity."""

    def filter(self, record: logging.LogRecord) -> bool:
        if (record.name == 'aiogram.dispatcher'
                and record.levelno == logging.ERROR
                and record.msg == 'Failed to fetch updates - %s: %s'
                and isinstance(record.args, tuple)
                and len(record.args) == 2
                and isinstance(record.args[1], (exceptions.TelegramNetworkError,
                                                exceptions.TelegramServerError))):
            record.levelno = logging.WARNING
            record.levelname = 'WARNING'
        return True


def configure_polling_logging() -> None:
    # Polling already retries connection/DNS failures with backoff. Its INFO
    # recovery message should be visible alongside the warnings about outages.
    logger = logging.getLogger('aiogram.dispatcher')
    logger.setLevel(logging.INFO)
    if not any(isinstance(item, TransientPollingErrorFilter) for item in logger.filters):
        logger.addFilter(TransientPollingErrorFilter())
