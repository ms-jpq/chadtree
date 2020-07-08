from __future__ import annotations

from dataclasses import dataclass
from os import listdir, stat
from os.path import basename, join, splitext
from stat import S_ISDIR, S_ISLNK
from typing import Iterable, List, Optional, Union, cast


@dataclass
class FSStat:
    is_link: bool
    is_dir: bool


@dataclass
class File:
    path: str
    is_link: bool
    name: str
    ext: str


@dataclass
class Dir:
    path: str
    is_link: bool
    name: str
    files: Optional[Iterable[File]]
    children: Optional[Iterable[Dir]]


Node = Union[File, Dir]


def fs_stat(path: str) -> FSStat:
    info = stat(path, follow_symlinks=False)
    is_link = S_ISLNK(info.st_mode)
    if is_link:
        link_info = stat(path, follow_symlinks=True)
        is_dir = S_ISDIR(link_info.st_mode)
        return FSStat(is_link=True, is_dir=is_dir)
    else:
        is_dir = S_ISDIR(info.st_mode)
        return FSStat(is_link=False, is_dir=is_dir)


def parse(root: str, *, max_depth: int, depth: int = 0) -> Node:
    info = fs_stat(root)
    name = basename(root)
    if not info.is_dir:
        _, ext = splitext(name)
        return File(path=root, is_link=info.is_link, name=name, ext=ext[1:])
    elif depth < max_depth:
        files: List[File] = []
        children: List[Dir] = []
        for el in listdir(root):
            child = parse(join(root, el), max_depth=max_depth, depth=depth + 1)
            if type(child) is File:
                files.append(cast(File, child))
            else:
                children.append(cast(Dir, child))
        return Dir(
            path=root, is_link=info.is_link, name=name, files=files, children=children
        )
    else:
        return Dir(
            path=root, is_link=info.is_link, name=name, files=None, children=None,
        )
