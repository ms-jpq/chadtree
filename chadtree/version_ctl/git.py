from concurrent.futures import Future, wait
from itertools import chain
from locale import strxfrm
from os import environ, linesep, sep
from pathlib import PurePath
from shlex import join
from shutil import which
from string import whitespace
from subprocess import DEVNULL, PIPE, CalledProcessError, check_output
from typing import (
    Any,
    Iterable,
    Iterator,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Tuple,
    cast,
)

from std2.string import removeprefix, removesuffix

from ..fs.ops import ancestors
from ..registry import pool
from .types import VCStatus

_WHITE_SPACES = {*whitespace}
_GIT_LIST_CMD = ("git", "status", "--ignored", "--renames", "--porcelain", "-z")
_GIT_ENV = {"LC_ALL": "C"}

_GIT_SUBMODULE_MARKER = "Entering "
_SUBMODULE_MARKER = "S"
_IGNORED_MARKER = "I"
_UNTRACKED_MARKER = "?"


def root(cwd: PurePath) -> PurePath:
    stdout = check_output(
        ("git", "rev-parse", "--show-toplevel"), stderr=PIPE, text=True, cwd=cwd
    )
    return PurePath(stdout.rstrip())


def _stat_main(cwd: str) -> Sequence[Tuple[str, PurePath]]:
    stdout = check_output(_GIT_LIST_CMD, stdin=DEVNULL, stderr=PIPE, text=True, cwd=cwd)

    def cont() -> Iterator[Tuple[str, PurePath]]:
        it = iter(stdout.split("\0"))
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, PurePath(file)

            if "R" in prefix:
                next(it, None)

    return tuple(cont())


def _stat_sub_modules(cwd: PurePath) -> Sequence[Tuple[str, PurePath]]:
    stdout = check_output(
        (
            "git",
            "submodule",
            "foreach",
            "--recursive",
            join(_GIT_LIST_CMD),
        ),
        env={**environ, **_GIT_ENV},
        stdin=DEVNULL,
        stderr=PIPE,
        text=True,
        cwd=cwd,
    )

    def cont() -> Iterator[Tuple[str, PurePath]]:
        it = iter(stdout)
        sub_module = PurePath(sep)
        acc: MutableSequence[str] = []

        for char in it:
            if char == linesep:
                line = "".join(acc)
                acc.clear()

                if not line.startswith(_GIT_SUBMODULE_MARKER):
                    raise ValueError(stdout)
                else:
                    quoted = removeprefix(line, prefix=_GIT_SUBMODULE_MARKER)
                    if not (quoted.startswith("'") and quoted.endswith("'")):
                        raise ValueError(stdout)
                    else:
                        sub_module = PurePath(
                            removesuffix(removeprefix(quoted, prefix="'"), suffix="'")
                        )
                        yield _SUBMODULE_MARKER, sub_module

            elif char == "\0":
                line = "".join(acc)
                acc.clear()

                if not sub_module:
                    raise ValueError(stdout)
                else:
                    prefix, file = line[:2], line[3:]
                    yield prefix, sub_module / file

                    if "R" in prefix:
                        next(it, None)
            else:
                acc.append(char)

    return tuple(cont())


def _stat_name(stat: str) -> str:
    markers = {
        "!!": _IGNORED_MARKER,
        "??": _UNTRACKED_MARKER,
    }
    return markers.get(stat, stat)


def _parse(root: PurePath, stats: Iterable[Tuple[str, PurePath]]) -> VCStatus:
    above = ancestors(root)
    ignored: MutableSet[PurePath] = set()
    status: MutableMapping[PurePath, str] = {}
    directories: MutableMapping[PurePath, MutableSet[str]] = {}

    for stat, name in stats:
        path = root / name
        status[path] = _stat_name(stat)
        if "!" in stat:
            ignored.add(path)
        else:
            for ancestor in ancestors(path):
                parents = directories.setdefault(ancestor, set())
                if stat != _SUBMODULE_MARKER:
                    for sym in stat:
                        parents.add(sym)

    for directory, syms in directories.items():
        pre_existing = {*status.get(directory, "")}
        symbols = pre_existing | syms - _WHITE_SPACES
        consoildated = sorted(symbols, key=strxfrm)
        status[directory] = "".join(consoildated)

    trimmed = {path: stat for path, stat in status.items() if path not in above}
    return VCStatus(ignored=ignored, status=trimmed)


def status(cwd: PurePath) -> VCStatus:
    if which("git"):
        try:
            r = pool.submit(root, cwd=cwd)
            s_main = pool.submit(_stat_main, cwd=cwd)
            s_sub = pool.submit(_stat_sub_modules, cwd=cwd)

            wait(cast(Sequence[Future[Any]], (r, s_main, s_sub)))
            return _parse(r.result(), stats=chain(s_main.result(), s_sub.result()))
        except CalledProcessError:
            return VCStatus()
    else:
        return VCStatus()

