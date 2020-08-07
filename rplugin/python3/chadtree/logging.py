from logging import DEBUG, ERROR, FATAL, INFO, WARN, getLogger
from typing import Any, Dict

from pynvim import Nvim

from .consts import __log_file__

LOGGER_NAME = "CHADTree"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

LEVELS: Dict[str, int] = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARN": WARN,
    "ERROR": ERROR,
    "FATAL": FATAL,
}


def setup(nvim: Nvim, level: str) -> None:
    pass


def debug(msg: Any, *args: Any, **kwargs: Any) -> None:
    logger = getLogger(LOGGER_NAME)
    logger.debug(msg, *args, **kwargs)


def info(msg: Any, *args: Any, **kwargs: Any) -> None:
    logger = getLogger(LOGGER_NAME)
    logger.info(msg, *args, **kwargs)


def warn(msg: Any, *args: Any, **kwargs: Any) -> None:
    logger = getLogger(LOGGER_NAME)
    logger.warn(msg, *args, **kwargs)


def error(msg: Any, *args: Any, **kwargs: Any) -> None:
    logger = getLogger(LOGGER_NAME)
    logger.error(msg, *args, **kwargs)


def fatal(msg: Any, *args: Any, **kwargs: Any) -> None:
    logger = getLogger(LOGGER_NAME)
    logger.fatal(msg, *args, **kwargs)
