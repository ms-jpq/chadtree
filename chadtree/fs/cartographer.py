from asyncio import gather
from contextlib import suppress
from fnmatch import fnmatch
from os import scandir, stat, stat_result
from os.path import normcase
from pathlib import Path, PurePath
from stat import (
    S_IFDOOR,
    S_ISBLK,
    S_ISCHR,
    S_ISDIR,
    S_ISFIFO,
    S_ISGID,
    S_ISLNK,
    S_ISREG,
    S_ISSOCK,
    S_ISUID,
    S_ISVTX,
    S_IWOTH,
    S_IXUSR,
)
from typing import AbstractSet, Iterator, Mapping, Optional, Sequence, Tuple

from std2.asyncio import pure, to_thread

from ..state.types import Index
from ..timeit import timeit
from .ops import ancestors
from .types import Ignored, Mode, Node

_FILE_MODES: Mapping[int, Mode] = {
    S_IXUSR: Mode.executable,
    S_IFDOOR: Mode.door,
    S_ISGID: Mode.set_gid,
    S_ISUID: Mode.set_uid,
    S_ISVTX: Mode.sticky,
    S_IWOTH: Mode.other_writable,
    S_IWOTH | S_ISVTX: Mode.sticky_other_writable,
}


def _fs_modes(stat: stat_result) -> Iterator[Mode]:
    st_mode = stat.st_mode
    if S_ISDIR(st_mode):
        yield Mode.folder
    if S_ISREG(st_mode):
        yield Mode.file
    if S_ISFIFO(st_mode):
        yield Mode.pipe
    if S_ISSOCK(st_mode):
        yield Mode.socket
    if S_ISCHR(st_mode):
        yield Mode.char_device
    if S_ISBLK(st_mode):
        yield Mode.block_device
    if stat.st_nlink > 1:
        yield Mode.multi_hardlink
    for bit, mode in _FILE_MODES.items():
        if bit and st_mode & bit == bit:
            yield mode


async def _fs_stat(path: PurePath) -> Tuple[AbstractSet[Mode], Optional[PurePath]]:
    def cont() -> Tuple[AbstractSet[Mode], Optional[PurePath]]:
        try:
            info = stat(path, follow_symlinks=False)
        except FileNotFoundError:
            return {Mode.orphan_link}, None
        else:
            if S_ISLNK(info.st_mode):
                try:
                    pointed = Path(path).resolve(strict=True)
                    link_info = stat(pointed, follow_symlinks=False)
                except (FileNotFoundError, NotADirectoryError, RuntimeError):
                    return {Mode.orphan_link}, None
                else:
                    mode = {*_fs_modes(link_info)}
                    return mode | {Mode.link}, pointed
            else:
                mode = {*_fs_modes(info)}
                return mode, None

    return await to_thread(cont)


async def _iterdir(dir: PurePath) -> Sequence[PurePath]:
    def cont() -> Sequence[PurePath]:
        with suppress(NotADirectoryError, FileNotFoundError):
            with scandir(dir) as it:
                return tuple(map(PurePath, it))

        return ()

    return await to_thread(cont)


async def _next(root: PurePath, index: Index) -> Optional[Node]:
    with suppress(PermissionError):
        mode, pointed = await _fs_stat(root)
        _ancestors = ancestors(root)

        if root in index:
            paths = await _iterdir(root)
            walked = await gather(
                *(gather(pure(path), _next(path, index=index)) for path in paths)
            )
            children = {k: v for k, v in walked}
        else:
            children = {}

        node = Node(
            path=root,
            mode=mode,
            pointed=pointed,
            ancestors=_ancestors,
            children=children,
        )

        return node

    return None


def _orphan(root: PurePath) -> Node:
    node = Node(
        mode={Mode.orphan_link},
        path=root,
        pointed=root,
        ancestors=frozenset(),
        children={},
    )
    return node


async def new(root: PurePath, index: Index) -> Node:
    with timeit("fs->new"):
        if node := await _next(root, index=index):
            return node
        else:
            return _orphan(root)


async def _update(
    root: Node, index: Index, paths: AbstractSet[PurePath]
) -> Optional[Node]:
    if root.path in paths:
        return await _next(root.path, index=index)
    else:
        walked = await gather(
            *(
                gather(pure(k), _update(v, index=index, paths=paths))
                for k, v in root.children.items()
            )
        )
        children = {k: v for k, v in walked}
        return Node(
            path=root.path,
            mode=root.mode,
            pointed=root.pointed,
            ancestors=root.ancestors,
            children=children,
        )


def user_ignored(node: Node, ignores: Ignored) -> bool:
    return (
        node.path.name in ignores.name_exact
        or any(fnmatch(node.path.name, pattern) for pattern in ignores.name_glob)
        or any(fnmatch(normcase(node.path), pattern) for pattern in ignores.path_glob)
    )


async def update(root: Node, *, index: Index, paths: AbstractSet[PurePath]) -> Node:
    with timeit("fs->_update"):
        try:
            node = await _update(root, index=index, paths=paths)
        except FileNotFoundError:
            return await new(root.path, index=index)
        else:
            return node or _orphan(root.path)


def is_dir(node: Node) -> bool:
    return Mode.folder in node.mode
