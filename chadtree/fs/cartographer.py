from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from fnmatch import fnmatch
from os import DirEntry, scandir, stat, stat_result
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
from typing import (
    AbstractSet,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
    cast,
)

from std2.itertools import batched
from std2.pathlib import is_relative_to

from ..consts import BATCH_FACTOR
from ..state.executor import AsyncExecutor
from ..state.types import Index
from ..timeit import timeit
from .nt import is_junction
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


def _iter(
    dirent: Union[PurePath, DirEntry], follow: bool, index: Index, lv: int = 0
) -> Iterator[PurePath]:
    if not lv:
        yield PurePath(dirent)
    with suppress(NotADirectoryError, FileNotFoundError, PermissionError):
        with scandir(dirent) as dirents:
            for child in dirents:
                yield (path := PurePath(child))
                if child.is_dir(follow_symlinks=follow) and path in index:
                    yield from _iter(child, follow=follow, index=index, lv=lv + 1)


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


def _fs_stat(path: PurePath) -> Tuple[AbstractSet[Mode], Optional[PurePath]]:
    try:
        info = stat(path, follow_symlinks=False)
    except (FileNotFoundError, PermissionError):
        return {Mode.orphan_link}, None
    else:
        if S_ISLNK(info.st_mode) or is_junction(info):
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


def _fs_node(path: PurePath) -> Node:
    mode, pointed = _fs_stat(path)
    node = Node(
        path=path,
        mode=mode,
        pointed=pointed,
        children={},
    )
    return node


def _iter_single_nodes(
    th: ThreadPoolExecutor, root: PurePath, follow: bool, index: Index
) -> Iterator[Node]:
    with timeit("fs->_iter"):
        dir_stream = batched(_iter(root, index=index, follow=follow), n=BATCH_FACTOR)
        for seq in th.map(lambda x: tuple(map(_fs_node, x)), dir_stream):
            yield from seq


async def _new(
    th: ThreadPoolExecutor, root: PurePath, follow_links: bool, index: Index
) -> Node:
    nodes: MutableMapping[PurePath, Node] = {}

    for idx, node in enumerate(
        _iter_single_nodes(th, root=root, follow=follow_links, index=index), start=1
    ):
        if idx % BATCH_FACTOR == 0:
            await sleep(0)
        nodes[node.path] = node
        if parent := nodes.get(node.path.parent):
            if parent == node:
                continue
            cast(MutableMapping[PurePath, Node], parent.children)[node.path] = node

    return nodes[root]


def _cross_over(root: PurePath, invalid: PurePath) -> bool:
    return is_relative_to(root, invalid) or is_relative_to(invalid, root)


async def _update(
    th: ThreadPoolExecutor,
    root: Node,
    follow_links: bool,
    index: Index,
    invalidate_dirs: AbstractSet[PurePath],
) -> Node:
    if any((_cross_over(root.path, invalid=invalid) for invalid in invalidate_dirs)):
        return await _new(th, root=root.path, follow_links=follow_links, index=index)
    else:
        children: MutableMapping[PurePath, Node] = {}
        for path, node in root.children.items():
            new_node = await _update(
                th,
                root=node,
                follow_links=follow_links,
                index=index,
                invalidate_dirs=invalidate_dirs,
            )
            children[path] = new_node
        return Node(
            path=root.path,
            mode=root.mode,
            pointed=root.pointed,
            children=children,
        )


async def new(
    exec: AsyncExecutor, root: PurePath, follow_links: bool, index: Index
) -> Node:
    with timeit("fs->new"):
        return await exec.submit(
            _new(exec.threadpool, root=root, follow_links=follow_links, index=index)
        )


async def update(
    exec: AsyncExecutor,
    root: Node,
    *,
    follow_links: bool,
    index: Index,
    invalidate_dirs: AbstractSet[PurePath],
) -> Node:
    with timeit("fs->_update"):
        try:
            return await exec.submit(
                _update(
                    exec.threadpool,
                    root=root,
                    follow_links=follow_links,
                    index=index,
                    invalidate_dirs=invalidate_dirs,
                )
            )
        except FileNotFoundError:
            return await new(
                exec, follow_links=follow_links, root=root.path, index=index
            )


def user_ignored(node: Node, ignores: Ignored) -> bool:
    return (
        node.path.name in ignores.name_exact
        or any(fnmatch(node.path.name, pattern) for pattern in ignores.name_glob)
        or any(fnmatch(normcase(node.path), pattern) for pattern in ignores.path_glob)
    )


def is_dir(node: Node) -> bool:
    return Mode.folder in node.mode


def act_like_dir(node: Node, follow_links: bool) -> bool:
    if node.pointed and not follow_links:
        return False
    else:
        return is_dir(node)
