from asyncio import get_running_loop
from os import listdir, stat
from os.path import basename, join, splitext
from stat import S_ISDIR, S_ISLNK
from typing import Dict, Set, cast

from .types import Index, Mode, Node


def fs_stat(path: str) -> Set[Mode]:
    info = stat(path, follow_symlinks=False)
    if S_ISLNK(info.st_mode):
        link_info = stat(path, follow_symlinks=True)
        mode = Mode.folder if S_ISDIR(link_info.st_mode) else Mode.file
        return {mode} | {Mode.link}
    else:
        mode = Mode.folder if S_ISDIR(info.st_mode) else Mode.file
        return {mode}


def _new(root: str, index: Index) -> Node:
    mode = fs_stat(root)
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
    loop = get_running_loop()
    return await loop.run_in_executor(None, _new, root, index)


def _update(root: Node, index: Index, paths: Set[str]) -> Node:
    if root.path in paths:
        return _new(root.path, index=index)
    else:
        children = {
            k: _update(v, index=index, paths=paths)
            for k, v in (root.children or cast(Dict[str, Node], {})).items()
        }
        return Node(
            path=root.path,
            mode=root.mode,
            name=root.name,
            children=children,
            ext=root.ext,
        )


async def update(root: Node, *, index: Index, paths: Set[str]) -> Node:
    loop = get_running_loop()
    try:
        return await loop.run_in_executor(None, _update, root, index, paths)
    except FileNotFoundError:
        return await new(root.path, index=index)
