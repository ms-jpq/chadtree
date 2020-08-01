from asyncio import gather
from locale import strxfrm
from os.path import join, sep
from shutil import which
from typing import Dict, Iterator, Set, Tuple

from .da import call
from .fs import ancestors
from .types import VCStatus


class GitError(Exception):
    pass


async def root() -> str:
    ret = await call("git", "rev-parse", "--show-toplevel")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        return ret.out.rstrip()


async def stat() -> Dict[str, str]:
    ret = await call("git", "status", "--ignored", "--renames", "--porcelain", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:

        def items() -> Iterator[Tuple[str, str]]:
            it = iter(ret.out.split("\0"))
            for line in it:
                prefix, file = line[:2], line[3:]
                yield prefix, file.rstrip(sep)
                if "R" in prefix:
                    next(it, None)

        entries = {file: prefix for prefix, file in items()}
        return entries


def parse(root: str, stats: Dict[str, str]) -> VCStatus:
    ignored: Set[str] = set()
    status: Dict[str, str] = {}
    directories: Dict[str, Set[str]] = {}

    for name, stat in stats.items():
        path = join(root, name)
        status[path] = stat
        if "!" in stat:
            ignored.add(path)
        else:
            for ancestor in ancestors(path):
                aggregate = directories.setdefault(ancestor, set())
                aggregate.update(stat)

    for directory, syms in directories.items():
        symbols = sorted((s for s in syms if s != " "), key=strxfrm)
        status[directory] = "".join(symbols)

    return VCStatus(ignored=ignored, status=status)


async def status() -> VCStatus:
    if which("git"):
        try:
            r, stats = await gather(root(), stat())
            return parse(r, stats)
        except GitError:
            return VCStatus()
    else:
        return VCStatus()
