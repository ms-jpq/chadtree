from locale import strxfrm
from os import environ, linesep
from os.path import join, sep
from shlex import join as sh_join
from shutil import which
from string import whitespace
from subprocess import DEVNULL, PIPE, CalledProcessError, check_output
from typing import Iterator, Mapping, MutableMapping, MutableSequence, Set, Tuple
from std2.string import removeprefix, removesuffix
from std2.concurrent.futures import gather

from ..fs.ops import ancestors
from ..registry import pool
from .types import VCStatus

_WHITE_SPACES = {*whitespace}
_GIT_LIST_CMD = ("git", "status", "--ignored", "--renames", "--porcelain", "-z")
_GIT_SUBMODULE_MARKER = "Entering "
_GIT_ENV = {"LC_ALL": "C"}


def _root(cwd: str) -> str:
    stdout = check_output(
        ("git", "rev-parse", "--show-toplevel"), stderr=PIPE, text=True, cwd=cwd
    )
    return stdout.rstrip()


def _stat_main(cwd: str) -> Mapping[str, str]:
    stdout = check_output(_GIT_LIST_CMD, stdin=DEVNULL, stderr=PIPE, text=True, cwd=cwd)

    def cont() -> Iterator[Tuple[str, str]]:
        it = iter(stdout.split("\0"))
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, file.rstrip(sep)
            if "R" in prefix:
                next(it, None)

    entries = {file: prefix for prefix, file in cont()}
    return entries


def _stat_sub_modules(cwd: str) -> Mapping[str, str]:
    stdout = check_output(
        (
            "git",
            "submodule",
            "foreach",
            "--recursive",
            sh_join(_GIT_LIST_CMD),
        ),
        env={**environ, **_GIT_ENV},
        stdin=DEVNULL,
        stderr=PIPE,
        text=True,
        cwd=cwd,
    )

    def cont() -> Iterator[Tuple[str, str]]:
        it = iter(stdout)
        root = ""
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
                        root = removesuffix(
                            removeprefix(quoted, prefix="'"), suffix="'"
                        )

            elif char == "\0":
                line = "".join(acc)
                acc.clear()

                if not root:
                    raise ValueError(stdout)
                else:
                    prefix, file = line[:2], line[3:]
                    yield prefix, join(root, file.rstrip(sep))
                    if "R" in prefix:
                        next(it, None)
            else:
                acc.append(char)

    entries = {file: prefix for prefix, file in cont()}
    return entries


def _stat_name(stat: str) -> str:
    if stat == "!!":
        return "I"
    else:
        return stat


def _parse(root: str, stats: Mapping[str, str]) -> VCStatus:
    ignored: Set[str] = set()
    status: MutableMapping[str, str] = {}
    directories: MutableMapping[str, Set[str]] = {}

    for name, stat in stats.items():
        path = join(root, name)
        status[path] = _stat_name(stat)
        if "!" in stat:
            ignored.add(path)
        else:
            for ancestor in ancestors(path):
                aggregate = directories.setdefault(ancestor, set())
                aggregate.update(stat)

    for directory, syms in directories.items():
        symbols = sorted(syms - _WHITE_SPACES, key=strxfrm)
        status[directory] = "".join(symbols)

    return VCStatus(ignored=ignored, status=status)


def status(cwd: str) -> VCStatus:
    if which("git"):
        try:
            ret: Tuple[str, Mapping[str, str], Mapping[str, str]] = gather(
                pool.submit(_root, cwd=cwd),
                pool.submit(_stat_main, cwd=cwd),
                pool.submit(_stat_sub_modules, cwd=cwd),
            )
            r, s_main, s_sub = ret
            stats = {**s_sub, **s_main}
            return _parse(r, stats)
        except CalledProcessError:
            return VCStatus()
    else:
        return VCStatus()
