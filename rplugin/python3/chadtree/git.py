from asyncio import gather
from locale import strxfrm
from os.path import join, sep
from shutil import which
from typing import Dict, Iterator, Set, Tuple

from .da import call
from .fs import ancestors
from .types import VCStatus

GIT_LIST_CMD = ("git", "status", "--ignored", "--renames", "--porcelain", "-z")
GIT_SUBMODULE_MARKER = "Entering "


class GitError(Exception):
    pass


async def root() -> str:
    ret = await call("git", "rev-parse", "--show-toplevel")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        return ret.out.rstrip()


async def stat_main() -> Dict[str, str]:
    ret = await call("git", "status", "--ignored", "--renames", "--porcelain", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        it = iter(ret.out.split("\0"))

        def cont() -> Iterator[Tuple[str, str]]:
            for line in it:
                prefix, file = line[:2], line[3:]
                yield prefix, file.rstrip(sep)
                if "R" in prefix:
                    next(it, None)

        entries = {file: prefix for prefix, file in cont()}
        return entries


async def stat_sub_modules() -> Dict[str, str]:
    ret = await call(
        "git", "submodule", "foreach", "--recursive", " ".join(GIT_LIST_CMD)
    )
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        it = iter(ret.out.split("\0"))

        def cont() -> Iterator[Tuple[str, str]]:
            root = ""
            for line in it:
                if line.startswith(GIT_SUBMODULE_MARKER):
                    root = line[len(GIT_SUBMODULE_MARKER) + 1 : -1]
                else:
                    prefix, file = line[:2], line[3:]
                    yield prefix, join(root, file.rstrip(sep))
                    if "R" in prefix:
                        next(it, None)

        entries = {file: prefix for prefix, file in cont()}
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
            r, s_main, s_sub = await gather(root(), stat_main(), stat_sub_modules())
            stats = {**s_sub, **s_main}
            return parse(r, stats)
        except GitError:
            return VCStatus()
    else:
        return VCStatus()
