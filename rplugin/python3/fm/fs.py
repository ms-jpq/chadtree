# from shutil import move as fs_move
from __future__ import annotations

from os.path import dirname, sep
from typing import Iterator

from .types import Selection


def ancestors(path: str) -> Iterator[str]:
    if not path or path == sep:
        return
    else:
        parent = dirname(path)
        yield from ancestors(parent)
        yield parent


def unify(paths: Selection) -> Iterator[str]:
    for path in paths:
        if not any(a in paths for a in ancestors(path)):
            yield path


def rename(src: str, dest: str) -> None:
    pass


def remove(src: Selection, dest: str) -> None:
    pass


def move(src: Selection, dest: str) -> None:
    pass


def copy(src: Selection, dest: str) -> None:
    pass
