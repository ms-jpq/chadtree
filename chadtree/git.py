from asyncio import gather
from locale import strxfrm
from os import linesep
from os.path import join, sep
from shutil import which
from typing import Iterator, Mapping, Set, Tuple

from std2.asyncio.subprocess import call

from .fs import ancestors
from .types import VCStatus

_GIT_LIST_CMD = ("git", "status", "--ignored", "--renames", "--porcelain")
_GIT_SUBMODULE_MARKER = "Entering "
_GIT_ENV = {"LC_ALL": "C"}


class GitError(Exception):
    pass


async def _root() -> str:
    ret = await call("git", "rev-parse", "--show-toplevel")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        return ret.out.rstrip()


async def _stat_main() -> Mapping[str, str]:
    ret = await call(*_GIT_LIST_CMD, "-z")
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


async def _stat_sub_modules() -> Mapping[str, str]:
    ret = await call(
        "git",
        "submodule",
        "foreach",
        "--recursive",
        " ".join(_GIT_LIST_CMD),
        env=_GIT_ENV,
    )
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        it = iter(ret.out.split(linesep))

        def cont() -> Iterator[Tuple[str, str]]:
            root = ""
            for line in it:
                if line.startswith(_GIT_SUBMODULE_MARKER):
                    root = line[len(_GIT_SUBMODULE_MARKER) + 1 : -1].rstrip(linesep)
                else:
                    prefix, file = line[:2], line[3:]
                    yield prefix, join(root, file.rstrip(sep))
                    if "R" in prefix:
                        next(it, None)

        entries = {file: prefix for prefix, file in cont()}
        return entries


def _parse(root: str, stats: Mapping[str, str]) -> VCStatus:
    ignored: Set[str] = set()
    status: Mapping[str, str] = {}
    directories: Mapping[str, Set[str]] = {}

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
            r, s_main, s_sub = await gather(_root(), _stat_main(), _stat_sub_modules())
            stats = {**s_sub, **s_main}
            return _parse(r, stats)
        except GitError:
            return VCStatus()
    else:
        return VCStatus()
