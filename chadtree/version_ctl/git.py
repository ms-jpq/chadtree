from itertools import chain
from locale import strxfrm
from os import environ, linesep
from os.path import join, sep
from shlex import join as sh_join
from shutil import which
from string import whitespace
from subprocess import DEVNULL, PIPE, CalledProcessError, check_output
from typing import Iterable, Iterator, MutableMapping, MutableSequence, Set, Tuple

from std2.concurrent.futures import gather
from std2.string import removeprefix, removesuffix

from ..fs.ops import ancestors
from ..registry import pool
from .types import VCStatus

_WHITE_SPACES = {*whitespace}
_GIT_LIST_CMD = ("git", "status", "--ignored", "--renames", "--porcelain", "-z")
_GIT_SUBMODULE_MARKER = "Entering "
_GIT_ENV = {"LC_ALL": "C"}
_SUBMODULE_MARKER = "S"
_IGNORED_MARKER = "I"


def _root(cwd: str) -> str:
    stdout = check_output(
        ("git", "rev-parse", "--show-toplevel"), stderr=PIPE, text=True, cwd=cwd
    )
    return stdout.rstrip()


def _stat_main(cwd: str) -> Iterator[Tuple[str, str]]:
    stdout = check_output(_GIT_LIST_CMD, stdin=DEVNULL, stderr=PIPE, text=True, cwd=cwd)

    def cont() -> Iterator[Tuple[str, str]]:
        it = iter(stdout.split("\0"))
        for line in it:
            prefix, file = line[:2], line[3:]
            yield prefix, file.rstrip(sep)

            if "R" in prefix:
                next(it, None)

    return cont()


def _stat_sub_modules(cwd: str) -> Iterator[Tuple[str, str]]:
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
        sub_module = ""
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
                        sub_module = removesuffix(
                            removeprefix(quoted, prefix="'"), suffix="'"
                        )
                        yield _SUBMODULE_MARKER, sub_module

            elif char == "\0":
                line = "".join(acc)
                acc.clear()

                if not sub_module:
                    raise ValueError(stdout)
                else:
                    prefix, file = line[:2], line[3:]
                    yield prefix, join(sub_module, file.rstrip(sep))

                    if "R" in prefix:
                        next(it, None)
            else:
                acc.append(char)

    return cont()


def _stat_name(stat: str) -> str:
    if stat == "!!":
        return _IGNORED_MARKER
    else:
        return stat


def _parse(root: str, stats: Iterable[Tuple[str, str]]) -> VCStatus:
    ignored: Set[str] = set()
    status: MutableMapping[str, str] = {}
    directories: MutableMapping[str, Set[str]] = {}

    for stat, name in stats:
        path = join(root, name)
        status[path] = _stat_name(stat)
        if "!" in stat:
            ignored.add(path)
        else:
            for ancestor in ancestors(path):
                parents = directories.setdefault(ancestor, set())
                if stat != _SUBMODULE_MARKER:
                    parents.update(stat)

    for directory, syms in directories.items():
        pre_existing = {*status.get(directory, "")}
        symbols = pre_existing | syms - _WHITE_SPACES
        consoildated = sorted(symbols, key=strxfrm)
        status[directory] = "".join(consoildated)

    return VCStatus(ignored=ignored, status=status)


def status(cwd: str) -> VCStatus:
    if which("git"):
        try:
            ret: Tuple[
                str, Iterator[Tuple[str, str]], Iterator[Tuple[str, str]]
            ] = gather(
                pool.submit(_root, cwd=cwd),
                pool.submit(_stat_main, cwd=cwd),
                pool.submit(_stat_sub_modules, cwd=cwd),
            )
            r, s_main, s_sub = ret
            return _parse(r, stats=chain(s_main, s_sub))
        except CalledProcessError:
            return VCStatus()
    else:
        return VCStatus()
