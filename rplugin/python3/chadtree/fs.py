from asyncio import get_running_loop
from dataclasses import dataclass
from datetime import datetime
from grp import getgrgid
from os import makedirs, readlink
from os import remove as rm
from os import stat
from os.path import dirname, exists, isdir, sep
from pathlib import Path
from pwd import getpwuid
from shutil import copy2, copytree
from shutil import move as mv
from shutil import rmtree
from stat import S_ISDIR, S_ISLNK, filemode
from typing import Dict, Iterable, Iterator, Optional, Set

from .consts import file_mode, folder_mode


def ancestors(path: str) -> Iterator[str]:
    if not path:
        return
    parent = dirname(path)
    if path == parent:
        return
    else:
        yield from ancestors(parent)
        yield parent


def is_parent(*, parent: str, child: str) -> bool:
    return any(parent == ancestor for ancestor in ancestors(child))


def unify_ancestors(paths: Set[str]) -> Iterator[str]:
    for path in paths:
        if not any(a in paths for a in ancestors(path)):
            yield path


async def fs_exists(path: str) -> bool:
    loop = get_running_loop()

    def cont() -> bool:
        return exists(path)

    return await loop.run_in_executor(None, cont)


@dataclass(frozen=True)
class FSstat:
    permissions: str
    user: str
    group: str
    date_mod: datetime
    size: int
    link: Optional[str]


def get_username(uid: int) -> str:
    try:
        return getpwuid(uid).pw_name
    except KeyError:
        return str(uid)


def get_groupname(gid: int) -> str:
    try:
        return getgrgid(gid).gr_name
    except KeyError:
        return str(gid)


def _fs_stat(path: str) -> FSstat:
    stats = stat(path, follow_symlinks=False)
    permissions = filemode(stats.st_mode)
    user = get_username(stats.st_uid)
    group = get_groupname(stats.st_gid)
    date_mod = datetime.fromtimestamp(stats.st_mtime)
    size = stats.st_size
    link = readlink(path) if S_ISLNK(stats.st_mode) else None
    fs_stat = FSstat(
        permissions=permissions,
        user=user,
        group=group,
        date_mod=date_mod,
        size=size,
        link=link,
    )
    return fs_stat


async def fs_stat(path: str) -> FSstat:
    loop = get_running_loop()

    def cont() -> FSstat:
        return _fs_stat(path)

    return await loop.run_in_executor(None, cont)


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
    stats = stat(src, follow_symlinks=False)
    if S_ISDIR(stats.st_mode):
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
