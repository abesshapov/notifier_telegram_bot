"""Methods for working with logger."""

import logging

from app.pkg.settings import settings

_log_format = (
    "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%("
    "funcName)s(%(lineno)d) - %(message)s "
)


def get_stream_handler():
    """Get stream handler for logger."""

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    """Get logger.

    Args:
        name:
            Name of the logger.

    Returns:
        LoggerLevel instance.

    Examples:
        ::

            >>> from app.pkg.logger import get_logger
            >>> logger = get_logger(__name__)
            >>> logger.info("Hello, World!")
            2021-01-01 00:00:00,000 - [INFO] - app.pkg.logger - (logger.py).get_logger(43) - Hello, World!  # pylint: disable=line-too-long
    """
    logger = logging.getLogger(name)
    logger.addHandler(get_stream_handler())
    logger.setLevel(settings.API.LOGGER.LEVEL.upper())
    return logger
