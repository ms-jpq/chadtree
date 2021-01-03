from os import listdir, stat
from os.path import basename, join, splitext
from stat import (
    S_IEXEC,
    S_ISDIR,
    S_ISFIFO,
    S_ISGID,
    S_ISLNK,
    S_ISREG,
    S_ISSOCK,
    S_ISUID,
    S_ISVTX,
    S_IWOTH,
)
from typing import Mapping, Iterator, Set, cast

from std2.asyncio import run_in_executor

from .types import Index, Mode, Node

FILE_MODES: Mapping[int, Mode] = {
    S_IEXEC: Mode.executable,
    S_IWOTH: Mode.other_writable,
    S_ISVTX: Mode.sticky_dir,
    S_ISGID: Mode.set_gid,
    S_ISUID: Mode.set_uid,
}


def _fs_modes(stat: int) -> Iterator[Mode]:
    if S_ISDIR(stat):
        yield Mode.folder
    if S_ISREG(stat):
        yield Mode.file
    if S_ISFIFO(stat):
        yield Mode.pipe
    if S_ISSOCK(stat):
        yield Mode.socket
    for bit, mode in FILE_MODES.items():
        if stat & bit == bit:
            yield mode


def _fs_stat(path: str) -> Set[Mode]:
    try:
        info = stat(path, follow_symlinks=False)
    except FileNotFoundError:
        return {Mode.orphan_link}
    else:
        if S_ISLNK(info.st_mode):
            try:
                link_info = stat(path, follow_symlinks=True)
            except FileNotFoundError:
                return {Mode.orphan_link}
            else:
                mode = {*_fs_modes(link_info.st_mode)}
                return mode | {Mode.link}
        else:
            mode = {*_fs_modes(info.st_mode)}
            return mode


def _new(root: str, index: Index) -> Node:
    mode = _fs_stat(root)
    name = basename(root)
    if Mode.folder not in mode:
        _, ext = splitext(name)
        return Node(path=root, mode=mode, name=name, ext=ext)

    elif root in index:
        children = {
            path: _new(path, index=index)
            for path in (join(root, d) for d in listdir(root))
        }
        return Node(path=root, mode=mode, name=name, children=children)
    else:
        return Node(path=root, mode=mode, name=name)


async def new(root: str, index: Index) -> Node:
    return await run_in_executor(_new, root, index)


def _update(root: Node, index: Index, paths: Set[str]) -> Node:
    if root.path in paths:
        return _new(root.path, index=index)
    else:
        children = {
            k: _update(v, index=index, paths=paths)
            for k, v in (root.children or cast(Mapping[str, Node], {})).items()
        }
        return Node(
            path=root.path,
            mode=root.mode,
            name=root.name,
            children=children,
            ext=root.ext,
        )


async def update(root: Node, *, index: Index, paths: Set[str]) -> Node:
    try:
        return await run_in_executor(_update, root, index, paths)
    except FileNotFoundError:
        return await new(root.path, index=index)
