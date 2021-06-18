from dataclasses import dataclass
from datetime import datetime
from os import makedirs
from os import name as os_name
from os import readlink
from os import remove as rm
from os import stat
from pathlib import Path, PurePath
from shutil import copy2, copytree
from shutil import move as mv
from shutil import rmtree
from stat import S_ISDIR, S_ISLNK, filemode
from typing import AbstractSet, Iterable, Mapping, Optional

from ..consts import FILE_MODE, FOLDER_MODE
from ..registry import pool


def ancestors(path: PurePath) -> AbstractSet[PurePath]:
    return {p for p in PurePath(path).parents}


def unify_ancestors(paths: AbstractSet[PurePath]) -> AbstractSet[PurePath]:
    return {p for p in paths if ancestors(p).isdisjoint(paths)}


@dataclass(frozen=True)
class FSstat:
    permissions: str
    user: str
    group: str
    date_mod: datetime
    size: int
    link: Optional[str]


if os_name == "nt":

    def _get_username(uid: int) -> str:
        return str(uid)

    def _get_groupname(gid: int) -> str:
        return str(gid)


else:
    from grp import getgrgid
    from pwd import getpwuid

    def _get_username(uid: int) -> str:
        try:
            return getpwuid(uid).pw_name
        except KeyError:
            return str(uid)

    def _get_groupname(gid: int) -> str:
        try:
            return getgrgid(gid).gr_name
        except KeyError:
            return str(gid)


def fs_stat(path: PurePath) -> FSstat:
    stats = stat(path, follow_symlinks=False)
    permissions = filemode(stats.st_mode)
    user = _get_username(stats.st_uid)
    group = _get_groupname(stats.st_gid)
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


def exists(path: PurePath, follow: bool) -> bool:
    try:
        stat(path, follow_symlinks=follow)
    except (OSError, ValueError):
        return False
    else:
        return True


def _mkdir(path: PurePath) -> None:
    makedirs(path, mode=FOLDER_MODE, exist_ok=True)


def mkdir(paths: Iterable[PurePath]) -> None:
    tuple(pool.map(_mkdir, paths))


def _new(path: PurePath) -> None:
    makedirs(path.parent, mode=FOLDER_MODE, exist_ok=True)
    Path(path).touch(mode=FILE_MODE, exist_ok=True)


def new(paths: Iterable[PurePath]) -> None:
    tuple(pool.map(_new, paths))


def _rename(src: PurePath, dest: PurePath) -> None:
    makedirs(dest.parent, mode=FOLDER_MODE, exist_ok=True)
    mv(str(src), str(dest))


def rename(operations: Mapping[PurePath, PurePath]) -> None:
    _op = lambda op: _rename(*op)
    tuple(pool.map(_op, operations.items()))


def _remove(path: PurePath) -> None:
    stats = stat(path, follow_symlinks=False)
    if S_ISDIR(stats.st_mode):
        rmtree(path)
    else:
        rm(path)


def remove(paths: Iterable[PurePath]) -> None:
    tuple(pool.map(_remove, paths))


def _cut(src: PurePath, dest: PurePath) -> None:
    mv(src, dest)


def cut(operations: Mapping[PurePath, PurePath]) -> None:
    _op = lambda op: _cut(*op)
    tuple(pool.map(_op, operations.items()))


def _copy(src: PurePath, dest: PurePath) -> None:
    stats = stat(src, follow_symlinks=False)
    if S_ISDIR(stats.st_mode):
        copytree(src, dest)
    else:
        copy2(src, dest, follow_symlinks=False)


def copy(operations: Mapping[PurePath, PurePath]) -> None:
    _op = lambda op: _copy(*op)
    tuple(pool.map(_op, operations.items()))

