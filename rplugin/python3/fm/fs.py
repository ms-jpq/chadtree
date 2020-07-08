from __future__ import annotations

from dataclasses import dataclass
from os import listdir, stat
from os.path import abspath, join, splitext
from stat import S_ISDIR, S_ISLNK
from typing import List, Union


@dataclass
class File:
    is_link: bool
    name: str
    ext: str


@dataclass
class Dir:
    is_link: bool
    name: str
    files: Union[List[File], None]
    children: Union[List[Dir], None]


@dataclass
class FSStat:
    is_link: bool
    is_dir: bool


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


def parse(root: str, *, max_depth: int, depth: int = 0) -> Union[File, Dir]:
    info = fs_stat(root)
    if not info.is_dir:
        name, ext = splitext(root)
        return File(is_link=info.is_link, name=name, ext=ext[1:])
    elif depth < max_depth:
        files: List[File] = []
        children: List[Dir] = []
        for el in listdir(root):
            child = parse(join(root, el), max_depth=max_depth, depth=depth + 1)
            if type(child) is File:
                files.append(child)
            else:
                children.append(child)
        return Dir(is_link=info.is_link, name=root, files=files, children=children)
    else:
        return Dir(is_link=info.is_link, name=root, files=None, children=None,)


def tree() -> Dir:
    root = abspath(".")
    ll = parse(root, max_depth=1)
    print(ll)

    return ""
