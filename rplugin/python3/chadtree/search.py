from itertools import chain
from os import environ
from os.path import join
from typing import Set

from .da import call
from .fs import ancestors, fs_exists


class SearchError(Exception):
    pass


async def search(args: str, cwd: str, sep: str) -> Set[str]:
    eshell = environ.get("SHELL")
    shell = eshell if eshell else "sh"
    ret = await call(shell, "-c", args, cwd=cwd)
    if ret.err:
        raise SearchError(ret.err)
    else:
        raw_lines = ret.out.split(sep)
        first_line = next(iter(raw_lines), "")
        if not await fs_exists(first_line):
            msg = f"Bad search results from {args}"
            raise SearchError(msg)
        else:
            lines = (join(cwd, line) for line in raw_lines if line)
            paths = {path for line in lines for path in chain(ancestors(line), (line,))}
            return paths
