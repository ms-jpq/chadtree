from dataclasses import dataclass
from os import environ
from os.path import join
from typing import Set

from .da import call


@dataclass(frozen=True)
class SearchResult:
    folders: Set[str]
    files: Set[str]


class SearchError(Exception):
    pass


async def search(args: str, cwd: str, sep: str) -> Set[str]:
    eshell = environ.get("SHELL")
    shell = eshell if eshell else "sh"
    ret = await call(shell, "-c", args, cwd=cwd)
    if ret.err:
        raise SearchError(ret.err)
    else:
        lines = {join(cwd, line) for line in ret.out.split(sep) if line}
        return lines
