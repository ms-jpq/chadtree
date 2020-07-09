from __future__ import annotations

from os import listdir, stat
from os.path import basename, join, splitext
from stat import S_ISDIR, S_ISLNK

from .types import Index, Mode, Node, Selection


def fs_stat(path: str) -> Mode:
    info = stat(path, follow_symlinks=False)
    if S_ISLNK(info.st_mode):
        link_info = stat(path, follow_symlinks=True)
        mode = Mode.FOLDER if S_ISDIR(link_info.st_mode) else Mode.FILE
        return mode | Mode.LINK
    else:
        mode = Mode.FOLDER if S_ISDIR(info.st_mode) else Mode.FILE
        return mode


def build(root: str, *, selection: Selection) -> Node:
    mode = fs_stat(root)
    name = basename(root)
    if Mode.FOLDER not in mode:
        _, ext = splitext(name)
        return Node(path=root, mode=mode, name=name, ext=ext)

    elif root in selection:
        children = {
            (path := join(root, d)): build(path, selection=selection)
            for d in listdir(root)
        }
        return Node(path=root, mode=mode, name=name, children=children)
    else:
        return Node(path=root, mode=mode, name=name)


def new(root: str, selection: Selection) -> Index:
    node = build(root, selection=selection)
    return Index(selection=selection, root=node)


def add(index: Index, selection: Selection) -> Index:
    pass


def remove(index: Index, selection: Selection) -> Index:
    pass
