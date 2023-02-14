from asyncio import Queue, gather
from contextlib import suppress
from fnmatch import fnmatch
from os import scandir, stat, stat_result
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
from typing import (
    AbstractSet,
    AsyncIterator,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    cast,
)

from std2.asyncio import to_thread
from std2.itertools import chunk

from ..consts import WALK_PARALLELISM_FACTOR
from ..state.types import Index
from .ops import ancestors, lock
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


def _listdir(path: PurePath) -> Iterator[Sequence[PurePath]]:
    with suppress(NotADirectoryError):
        with scandir(path) as it:
            chunked = chunk(it, WALK_PARALLELISM_FACTOR)
            while True:
                if chunks := next(chunked, None):
                    yield tuple(map(PurePath, chunks))
                else:
                    break


async def _next(
    roots: Iterable[PurePath], index: Index, acc: Queue, bfs_q: Queue
) -> None:
    for root in roots:
        with suppress(PermissionError):
            mode, pointed = await _fs_stat(root)
            _ancestors = ancestors(root)
            node = Node(
                path=root,
                mode=mode,
                pointed=pointed,
                ancestors=_ancestors,
            )
            await acc.put(node)

            if root in index:
                for paths in await to_thread(lambda: tuple(_listdir(root))):
                    await bfs_q.put(paths)


async def _join(nodes: Queue) -> Node:
    root_node: Optional[Node] = None
    acc: MutableMapping[PurePath, Node] = {}

    while not nodes.empty():
        node: Node = await nodes.get()
        path = node.path
        acc[path] = node

        parent = acc.get(path.parent)
        if not parent or parent.path == node.path:
            assert root_node is None
            root_node = node
        else:
            siblings = cast(MutableMapping[PurePath, Node], parent.children)
            siblings[path] = node

    if not root_node:
        assert False
    else:
        return root_node


async def _new(root: PurePath, index: Index) -> Node:
    acc: Queue = Queue()
    bfs_q: Queue = Queue()

    async def drain() -> AsyncIterator[Sequence[PurePath]]:
        while not bfs_q.empty():
            yield await bfs_q.get()

    await bfs_q.put((root,))
    while not bfs_q.empty():
        tasks = [
            _next(paths, index=index, acc=acc, bfs_q=bfs_q) async for paths in drain()
        ]
        await gather(*tasks)

    return await _join(acc)


async def new(root: PurePath, index: Index) -> Node:
    async with lock():
        return await _new(root, index=index)


async def _update(root: Node, index: Index, paths: AbstractSet[PurePath]) -> Node:
    if root.path in paths:
        return await _new(root.path, index=index)
    else:
        children = {
            k: await _update(v, index=index, paths=paths)
            for k, v in root.children.items()
        }
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
        or any(fnmatch(str(node.path), pattern) for pattern in ignores.path_glob)
    )


async def update(root: Node, *, index: Index, paths: AbstractSet[PurePath]) -> Node:
    async with lock():
        try:
            return await _update(root, index=index, paths=paths)
        except FileNotFoundError:
            return await _new(root.path, index=index)


def is_dir(node: Node) -> bool:
    return Mode.folder in node.mode
