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
from typing import FrozenSet, Iterable, Iterator, Mapping, Optional


from ..consts import FILE_MODE, FOLDER_MODE


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


def unify_ancestors(paths: FrozenSet[str]) -> Iterator[str]:
    for path in paths:
        if not any(a in paths for a in ancestors(path)):
            yield path


def fs_exists(path: str) -> bool:
    return exists(path)


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


def fs_stat(path: str) -> FSstat:
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


def new(dest: str) -> None:
    if dest.endswith(sep):
        makedirs(dest, mode=FOLDER_MODE, exist_ok=True)
    else:
        parent = dirname(dest)
        makedirs(parent, mode=FOLDER_MODE, exist_ok=True)
        Path(dest).touch(mode=FILE_MODE, exist_ok=True)


def rename(src: str, dest: str) -> None:
    parent = dirname(dest)
    makedirs(parent, mode=FOLDER_MODE, exist_ok=True)
    mv(src, dest)


def remove(paths: Iterable[str]) -> None:
    for path in paths:
        stats = stat(path, follow_symlinks=False)
        if S_ISDIR(stats.st_mode):
            rmtree(path)
        else:
            rm(path)


def cut(operations: Mapping[str, str]) -> None:
    for src, dest in operations.items():
        mv(src, dest)


def copy(operations: Mapping[str, str]) -> None:
    for src, dest in operations.items():
        stats = stat(src, follow_symlinks=False)
        if S_ISDIR(stats.st_mode):
            copytree(src, dest)
        else:
            copy2(src, dest)