from asyncio import get_running_loop
from os import makedirs
from os import remove as rm
from os.path import dirname, isdir, sep
from pathlib import Path
from shutil import copy2, copytree
from shutil import move as mv
from shutil import rmtree
from typing import Dict, Iterable, Iterator, Set

from .consts import file_mode, folder_mode


def is_parent(*, parent: str, child: str) -> bool:
    return child.startswith(parent)


def ancestors(path: str) -> Iterator[str]:
    if not path or path == sep:
        return
    else:
        parent = dirname(path)
        yield from ancestors(parent)
        yield parent


def unify(paths: Set[str]) -> Iterator[str]:
    for path in paths:
        if not any(a in paths for a in ancestors(path)):
            yield path


def _new(dest: str) -> None:
    if dest.endswith(sep):
        makedirs(dest, mode=folder_mode, exist_ok=True)
    else:
        parent = dirname(dest)
        makedirs(parent, mode=folder_mode, exist_ok=True)
        Path(dest).touch(mode=file_mode, exist_ok=True)


async def new(dest: str) -> None:
    loop = get_running_loop()

    def cont() -> None:
        _new(dest)

    await loop.run_in_executor(None, cont)


def _rename(src: str, dest: str) -> None:
    parent = dirname(dest)
    makedirs(parent, mode=folder_mode, exist_ok=True)
    mv(src, dest)


async def rename(src: str, dest: str) -> None:
    loop = get_running_loop()

    def cont() -> None:
        _rename(src, dest)

    await loop.run_in_executor(None, cont)


def _remove(src: str) -> None:
    if isdir(src):
        rmtree(src)
    else:
        rm(src)


async def remove(paths: Iterable[str]) -> None:
    loop = get_running_loop()

    def cont() -> None:
        for path in paths:
            _remove(path)

    await loop.run_in_executor(None, cont)


def _cut(src: str, dest: str) -> None:
    mv(src, dest)


async def cut(operations: Dict[str, str]) -> None:
    loop = get_running_loop()

    def cont() -> None:
        for src, dest in operations.items():
            _cut(src, dest)

    await loop.run_in_executor(None, cont)


def _copy(src: str, dest: str) -> None:
    if isdir(src):
        copytree(src, dest)
    else:
        copy2(src, dest)


async def copy(operations: Dict[str, str]) -> None:
    loop = get_running_loop()

    def cont() -> None:
        for src, dest in operations.items():
            _copy(src, dest)

    await loop.run_in_executor(None, cont)
