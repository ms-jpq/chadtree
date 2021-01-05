from dataclasses import dataclass
from datetime import datetime
from os import makedirs
from os import name as os_name
from os import readlink
from os import remove as rm
from os import stat
from os.path import dirname, exists, sep
from pathlib import Path
from shutil import copy2, copytree
from shutil import move as mv
from shutil import rmtree
from stat import S_ISDIR, S_ISLNK, filemode
from typing import Mapping, Iterable, Iterator, Optional, Set

from .consts import FILE_MODE, FOLDER_MODE
from std2.asyncio import run_in_executor


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
    def cont() -> bool:
        return exists(path)

    return await run_in_executor(cont)


@dataclass(frozen=True)
class FSstat:
    permissions: str
    user: str
    group: str
    date_mod: datetime
    size: int
    link: Optional[str]


if os_name == "nt":

    def get_username(uid: int) -> str:
        return str(uid)

    def get_groupname(gid: int) -> str:
        return str(gid)


else:
    from grp import getgrgid
    from pwd import getpwuid

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
    def cont() -> FSstat:
        return _fs_stat(path)

    return await run_in_executor(cont)


def _new(dest: str) -> None:
    if dest.endswith(sep):
        makedirs(dest, mode=FOLDER_MODE, exist_ok=True)
    else:
        parent = dirname(dest)
        makedirs(parent, mode=FOLDER_MODE, exist_ok=True)
        Path(dest).touch(mode=FILE_MODE, exist_ok=True)


async def new(dest: str) -> None:
    def cont() -> None:
        _new(dest)

    await run_in_executor(cont)


def _rename(src: str, dest: str) -> None:
    parent = dirname(dest)
    makedirs(parent, mode=FOLDER_MODE, exist_ok=True)
    mv(src, dest)


async def rename(src: str, dest: str) -> None:
    def cont() -> None:
        _rename(src, dest)

    await run_in_executor(cont)


def _remove(src: str) -> None:
    stats = stat(src, follow_symlinks=False)
    if S_ISDIR(stats.st_mode):
        rmtree(src)
    else:
        rm(src)


async def remove(paths: Iterable[str]) -> None:
    def cont() -> None:
        for path in paths:
            _remove(path)

    await run_in_executor(cont)


def _cut(src: str, dest: str) -> None:
    mv(src, dest)


async def cut(operations: Mapping[str, str]) -> None:
    def cont() -> None:
        for src, dest in operations.items():
            _cut(src, dest)

    await run_in_executor(cont)


def _copy(src: str, dest: str) -> None:
    stats = stat(src, follow_symlinks=False)
    if S_ISDIR(stats.st_mode):
        copytree(src, dest)
    else:
        copy2(src, dest)


async def copy(operations: Mapping[str, str]) -> None:
    def cont() -> None:
        for src, dest in operations.items():
            _copy(src, dest)

    await run_in_executor(cont)
