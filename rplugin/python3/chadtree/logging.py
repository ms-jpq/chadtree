from logging import DEBUG, ERROR, FATAL, INFO, WARN, basicConfig
from typing import Dict

from pynvim import Nvim

from .consts import __log_file__

DATE_FMT = "%Y-%m-%d %H:%M:%S"

LEVELS: Dict[str, int] = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARN": WARN,
    "ERROR": ERROR,
    "FATAL": FATAL,
}


def setup(nvim: Nvim, level: str) -> None:
    basicConfig(filename=__log_file__, datefmt=DATE_FMT, level=LEVELS.get(level, DEBUG))
