from locale import strxfrm
from os import environ, linesep
from os.path import join, sep
from shutil import which
from subprocess import DEVNULL, PIPE, run
from typing import Iterator, Mapping, MutableMapping, Set, Tuple

from std2.types import freeze

from ..fs.ops import ancestors
from .types import VCStatus

_GIT_LIST_CMD = ("git", "status", "--ignored", "--renames", "--porcelain")
_GIT_SUBMODULE_MARKER = "Entering "
_GIT_ENV = {"LC_ALL": "C"}


class _GitError(Exception):
    pass


def _root() -> str:
    ret = run(
        ("git", "rev-parse", "--show-toplevel"),
        stdin=DEVNULL,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    if ret.returncode != 0:
        raise _GitError(ret.stderr)
    else:
        return ret.stdout.rstrip()


def _stat_main() -> Mapping[str, str]:
    ret = run(
        tuple((*_GIT_LIST_CMD, "-z")),
        stdin=DEVNULL,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    if ret.returncode != 0:
        raise _GitError(ret.stderr)
    else:
        it = iter(ret.stdout.split("\0"))

        def cont() -> Iterator[Tuple[str, str]]:
            for line in it:
                prefix, file = line[:2], line[3:]
                yield prefix, file.rstrip(sep)
                if "R" in prefix:
                    next(it, None)

        entries = {file: prefix for prefix, file in cont()}
        return entries


def _stat_sub_modules() -> Mapping[str, str]:
    ret = run(
        ("git", "submodule", "foreach", "--recursive", " ".join(_GIT_LIST_CMD)),
        env={**environ, **_GIT_ENV},
        stdin=DEVNULL,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    if ret.returncode != 0:
        raise _GitError(ret.stderr)
    else:
        it = iter(ret.stdout.split(linesep))

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
    status: MutableMapping[str, str] = {}
    directories: MutableMapping[str, Set[str]] = {}

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

    return VCStatus(ignored=freeze(ignored), status=freeze(status))


def status() -> VCStatus:
    if which("git"):
        try:
            r, s_main, s_sub = _root(), _stat_main(), _stat_sub_modules()
            stats = {**s_sub, **s_main}
            return _parse(r, stats)
        except _GitError:
            return VCStatus()
    else:
        return VCStatus()