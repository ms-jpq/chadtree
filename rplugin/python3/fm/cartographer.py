from __future__ import annotations

from os import listdir, stat
from os.path import basename, join, splitext
from stat import S_ISDIR, S_ISLNK
from typing import Set

from .types import Index, Mode, Node


def fs_stat(path: str) -> Mode:
    info = stat(path, follow_symlinks=False)
    if S_ISLNK(info.st_mode):
        link_info = stat(path, follow_symlinks=True)
        mode = Mode.FOLDER if S_ISDIR(link_info.st_mode) else Mode.FILE
        return mode | Mode.LINK
    else:
        mode = Mode.FOLDER if S_ISDIR(info.st_mode) else Mode.FILE
        return mode


def new(root: str, *, index: Index) -> Node:
    mode = fs_stat(root)
    name = basename(root)
    if Mode.FOLDER not in mode:
        _, ext = splitext(name)
        return Node(path=root, mode=mode, name=name, ext=ext)

    elif root in index:
        children = {
            path: new(path, index=index)
            for path in (join(root, d) for d in listdir(root))
        }
        return Node(path=root, mode=mode, name=name, children=children)
    else:
        return Node(path=root, mode=mode, name=name)


def update(root: Node, *, index: Index, paths: Set[str]) -> Node:
    if root.path in paths:
        return new(root.path, index=index)
    else:
        children = {
            k: update(v, index=index, paths=paths)
            for k, v in (root.children or {}).items()
        }
        return Node(
            path=root.path,
            mode=root.mode,
            name=root.name,
            children=children,
            ext=root.ext,
        )
