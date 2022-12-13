from asyncio import gather
from functools import lru_cache
from itertools import chain
from locale import strxfrm
from os import environ, linesep
from pathlib import PurePath
from posixpath import sep
from string import whitespace
from subprocess import CalledProcessError
from typing import (
    Iterable,
    Iterator,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Tuple,
)

from pynvim_pp.lib import decode
from std2.asyncio.subprocess import call
from std2.pathlib import ROOT
from std2.string import removeprefix, removesuffix

from ..fs.ops import ancestors, which
from .types import VCStatus

_WHITE_SPACES = {*whitespace}
_GIT_LIST_CMD = (
    "--no-optional-locks",
    "status",
    "--ignored",
    "--renames",
    "--porcelain",
    "-z",
)
_GIT_ENV = {"LC_ALL": "C"}

_GIT_SUBMODULE_MARKER = "Entering "
_SUBMODULE_MARKER = "S"
_IGNORED_MARKER = "I"
_UNTRACKED_MARKER = "?"


@lru_cache(maxsize=6969)
def _path_conv(path: str) -> PurePath:
    if not which("cygpath"):
        return PurePath(path)
    else:
        splits = path.split(sep, maxsplit=2)
        print(splits)
        if len(splits) > 2:
            empty, drive, p = splits
            # assert not empty
            return PurePath(f"{drive}:") / p
        else:
            return PurePath(path)


async def root(git: PurePath, cwd: PurePath) -> PurePath:
    proc = await call(
        git,
        "--no-optional-locks",
        "rev-parse",
        "--show-toplevel",
        cwd=cwd,
    )
    return _path_conv(decode(proc.stdout.rstrip()))


async def _stat_main(git: PurePath, cwd: PurePath) -> Sequence[Tuple[str, PurePath]]:
    proc = await call(git, *_GIT_LIST_CMD, cwd=cwd)

    def cont() -> Iterator[Tuple[str, PurePath]]:
        it = iter(decode(proc.stdout).split("\0"))
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, _path_conv(file)

            if "R" in prefix:
                next(it, None)

    return tuple(cont())


async def _stat_sub_modules(
    git: PurePath, cwd: PurePath
) -> Sequence[Tuple[str, PurePath]]:
    proc = await call(
        git,
        "submodule",
        "foreach",
        "--recursive",
        git,
        *_GIT_LIST_CMD,
        env={**environ, **_GIT_ENV},
        cwd=cwd,
    )

    def cont() -> Iterator[Tuple[str, PurePath]]:
        stdout = decode(proc.stdout)
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
                        sub_module = _path_conv(
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


async def status(cwd: PurePath) -> VCStatus:
    if git := which("git"):
        bin = PurePath(git)
        try:
            git_root, *stats = await gather(
                root(bin, cwd=cwd),
                _stat_main(bin, cwd=cwd),
                _stat_sub_modules(bin, cwd=cwd),
            )
        except CalledProcessError:
            return VCStatus()
        else:
            return _parse(git_root, stats=chain.from_iterable(stats))
    else:
        return VCStatus()
