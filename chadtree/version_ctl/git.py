from asyncio import gather
from functools import lru_cache
from itertools import chain
from locale import strxfrm
from ntpath import altsep, sep
from os import linesep
from os.path import normpath
from pathlib import PurePath, PureWindowsPath
from string import whitespace
from subprocess import CalledProcessError
from typing import (
    Iterator,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Tuple,
)

from pynvim_pp.lib import encode
from std2.pathlib import ROOT
from std2.string import removeprefix, removesuffix

from ..fs.ops import ancestors, which
from .nice import nice_call
from .types import VCStatus

_Stats = Sequence[Tuple[str, PurePath]]

_WHITE_SPACES = {*whitespace}
_GIT_LIST_CMD = (
    "--no-optional-locks",
    "status",
    "--ignored",
    "--renames",
    "--porcelain",
    "-z",
)


_GIT_SUBMODULE_MARKER = "Entering "
_SUBMODULE_MARKER = "S"
_IGNORED_MARKER = "I"
_UNTRACKED_MARKER = "?"


async def root(git: PurePath, cwd: PurePath) -> PurePath:
    stdout = await nice_call(
        (git, "--no-optional-locks", "rev-parse", "--show-toplevel"), cwd=cwd
    )
    return PurePath(stdout.rstrip())


@lru_cache(maxsize=1)
def _parse_stats_main(stdout: str) -> Sequence[Tuple[str, PurePath]]:
    def cont() -> Iterator[Tuple[str, PurePath]]:
        it = iter(stdout.split("\0"))
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, PurePath(file)

            if "R" in prefix:
                next(it, None)

    return tuple(cont())


async def _stat_main(git: PurePath, cwd: PurePath) -> str:
    stdout = await nice_call((git, *_GIT_LIST_CMD), cwd=cwd)
    return stdout


@lru_cache(maxsize=1)
def _parse_sub_modules(stdout: str) -> Sequence[Tuple[str, PurePath]]:
    def cont() -> Iterator[Tuple[str, PurePath]]:
        it = iter(stdout)
        sub_module = ROOT
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


async def _stat_sub_modules(git: PurePath, cwd: PurePath) -> str:
    stdout = await nice_call(
        (git, "submodule", "foreach", "--recursive", git, *_GIT_LIST_CMD),
        cwd=cwd,
    )
    return stdout


def _stat_name(stat: str) -> str:
    markers = {
        "!!": _IGNORED_MARKER,
        "??": _UNTRACKED_MARKER,
    }
    return markers.get(stat, stat)


def _raw_conv(path: PurePath) -> str:
    return normpath(path).replace(sep, altsep)


async def _conv(raw_root: PurePath, raw_stats: _Stats) -> Tuple[PurePath, _Stats]:
    if (cygpath := which("cygpath")) and isinstance(raw_root, PureWindowsPath):
        stdout = await nice_call((cygpath, "--windows", "--", _raw_conv(raw_root)))
        root = PurePath(stdout.rstrip())
        stdin = encode("\n".join(map(_raw_conv, (path for _, path in raw_stats))))
        stdout = await nice_call(
            (cygpath, "--windows", "--absolute", "--file", "-"), cwd=root, stdin=stdin
        )
        stats = tuple(
            (stat, PurePath(path))
            for (stat, _), path in zip(raw_stats, stdout.splitlines())
        )
        return root, stats
    else:
        return raw_root, raw_stats


def _parse(root: PurePath, stats: _Stats) -> VCStatus:
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


async def status(cwd: PurePath, prev: VCStatus) -> VCStatus:
    if git := which("git"):
        bin = PurePath(git)
        try:
            raw_root, main, submodules = await gather(
                root(bin, cwd=cwd),
                _stat_main(bin, cwd=cwd),
                _stat_sub_modules(bin, cwd=cwd),
            )
            if main == prev.main and submodules == prev.submodules:
                return prev
            else:
                raw_stats = chain(
                    (_parse_stats_main(main)), _parse_sub_modules(submodules)
                )
                parsed_root, stats = await _conv(raw_root, raw_stats=tuple(raw_stats))
        except CalledProcessError:
            return VCStatus()
        else:
            return _parse(parsed_root, stats=stats)
    else:
        return VCStatus()
