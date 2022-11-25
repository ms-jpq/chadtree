from asyncio import Lock, Queue, gather
from contextlib import suppress
from fnmatch import fnmatch
from functools import lru_cache
from os import scandir, stat
from pathlib import PurePath
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
from typing import (
    AbstractSet,
    AsyncIterator,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    cast,
)

from std2.asyncio import to_thread
from std2.itertools import chunk

from ..consts import WALK_PARALLELISM_FACTOR
from ..state.types import Index
from .ops import ancestors, lock
from .types import Ignored, Mode, Node

_FILE_MODES: Mapping[int, Mode] = {
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
    for bit, mode in _FILE_MODES.items():
        if stat & bit == bit:
            yield mode


async def _fs_stat(path: PurePath) -> AbstractSet[Mode]:
    def cont() -> AbstractSet[Mode]:
        try:
            info = stat(path, follow_symlinks=False)
        except FileNotFoundError:
            return {Mode.orphan_link}
        else:
            if S_ISLNK(info.st_mode):
                try:
                    link_info = stat(path, follow_symlinks=True)
                except (FileNotFoundError, NotADirectoryError):
                    return {Mode.orphan_link}
                else:
                    mode = {*_fs_modes(link_info.st_mode)}
                    return mode | {Mode.link}
            else:
                mode = {*_fs_modes(info.st_mode)}
                return mode

    return await to_thread(cont)


async def _listdir(path: PurePath) -> AsyncIterator[Sequence[PurePath]]:
    with suppress(NotADirectoryError):
        with await to_thread(lambda: scandir(path)) as it:
            chunked = chunk(it, WALK_PARALLELISM_FACTOR)
            while True:
                if chunks := await to_thread(lambda: next(chunked, None)):
                    yield tuple(map(PurePath, chunks))
                else:
                    break


async def _next(
    roots: Iterable[PurePath], index: Index, acc: Queue, bfs_q: Queue
) -> None:
    for root in roots:
        with suppress(PermissionError):
            mode = await _fs_stat(root)
            _ancestors = ancestors(root)
            node = Node(
                path=root,
                mode=mode,
                ancestors=_ancestors,
            )
            await acc.put(node)

            if root in index:
                async for paths in _listdir(root):
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
