from logging import (
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    WARN,
    FileHandler,
    Formatter,
    StreamHandler,
    getLevelName,
    getLogger,
)
from typing import Dict

from pynvim import Nvim

from .consts import __log_file__

LOGGER_NAME = "CHADTree"

LOG_FMT = """\
--  {name}\t{levelname}\t{asctime}
module:   {module}
line:     {lineno}
function: {funcName}
message:  |-
{message}
"""

DATE_FMT = "%Y-%m-%d %H:%M:%S"

LEVELS: Dict[str, int] = {
    getLevelName(lv): lv for lv in (DEBUG, INFO, WARN, ERROR, FATAL)
}


def setup(nvim: Nvim, level: str) -> None:
    logger = getLogger(LOGGER_NAME)
    logger.setLevel(LEVELS.get(level, DEBUG))
    formatter = Formatter(fmt=LOG_FMT, datefmt=DATE_FMT, style="{")
    handlers = (StreamHandler(), FileHandler(filename=__log_file__))
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)


log = getLogger(LOGGER_NAME)
