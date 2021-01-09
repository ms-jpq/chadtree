from asyncio.subprocess import DEVNULL, PIPE
from typing import Set


class SearchError(Exception):
    pass


def search(args: str, cwd: str, sep: str) -> Set[str]:
    raise SearchError()
