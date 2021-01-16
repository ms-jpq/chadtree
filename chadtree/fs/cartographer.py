from os import listdir, stat
from os.path import basename, dirname, join, splitext
from queue import SimpleQueue
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
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    cast,
)

from std2.concurrent.futures import gather
from std2.itertools import chunk

from ..consts import WALK_PARALLELISM_FACTOR
from ..registry import pool
from ..state.types import Index
from .types import Mode, Node

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


def _fs_stat(path: str) -> AbstractSet[Mode]:
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


def _new(
    roots: Iterable[str], index: Index, acc: SimpleQueue, bfs_q: SimpleQueue
) -> None:
    for root in roots:
        mode = _fs_stat(root)
        name = basename(root)
        _, _ext = splitext(name)
        ext = None if Mode.folder in mode else _ext
        node = Node(path=root, mode=mode, name=name, ext=ext)
        acc.put(node)

        if root in index:
            for item in listdir(root):
                path = join(root, item)
                bfs_q.put(path)


def _join(nodes: SimpleQueue) -> Node:
    root_node: Optional[Node] = None
    acc: MutableMapping[str, Node] = {}

    while not nodes.empty():
        node: Node = nodes.get()
        path = node.path
        acc[path] = node

        parent = acc.get(dirname(path))
        if not parent:
            assert root_node is None
            root_node = node
        else:
            siblings = cast(MutableMapping[str, Node], parent.children)
            siblings[path] = node

    if not root_node:
        assert False
    else:
        return root_node


def new(root: str, index: Index) -> Node:
    acc: SimpleQueue = SimpleQueue()
    bfs_q: SimpleQueue = SimpleQueue()

    def drain() -> Iterator[str]:
        while not bfs_q.empty():
            yield bfs_q.get()

    _new((root,), index=index, acc=acc, bfs_q=bfs_q)
    while not bfs_q.empty():
        tasks = (
            pool.submit(_new, roots=paths, index=index, acc=acc, bfs_q=bfs_q)
            for paths in chunk(drain(), n=WALK_PARALLELISM_FACTOR)
        )
        gather(*tasks)

    return _join(acc)


def _update(root: Node, index: Index, paths: AbstractSet[str]) -> Node:
    if root.path in paths:
        return new(root.path, index=index)
    else:
        children = {
            k: _update(v, index=index, paths=paths) for k, v in root.children.items()
        }
        return Node(
            path=root.path,
            mode=root.mode,
            name=root.name,
            children=children,
            ext=root.ext,
        )


def update(root: Node, *, index: Index, paths: AbstractSet[str]) -> Node:
    try:
        return _update(root, index=index, paths=paths)
    except FileNotFoundError:
        return new(root.path, index=index)


def is_dir(node: Node) -> bool:
    return Mode.folder in node.mode
