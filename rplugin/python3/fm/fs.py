from __future__ import annotations

from os import makedirs
from os import remove as rm
from os.path import basename, dirname, isdir, join, sep
from pathlib import Path
from shutil import copy2, copytree
from shutil import move as mv
from shutil import rmtree
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


def new(dest: str, folder_mode: int = 0o755, file_mode: int = 0o644) -> None:
    if dest.endswith(sep):
        makedirs(dest, mode=folder_mode, exist_ok=True)
    else:
        parent = dirname(dest)
        makedirs(parent, mode=folder_mode, exist_ok=True)
        Path(dest).touch(mode=file_mode, exist_ok=True)


def rename(src: str, dest: str) -> None:
    mv(src, dest)


def remove(src: Selection) -> None:
    for path in unify(src):
        if isdir(path):
            rmtree(path)
        else:
            rm(path)


def move(src: Selection, dest: str) -> None:
    dst_dir = dest if isdir(dest) else dirname(dest)
    for path in unify(src):
        name = basename(path)
        dst = join(dst_dir, name)
        mv(path, dst)


def copy(src: Selection, dest: str) -> None:
    dst_dir = dest if isdir(dest) else dirname(dest)
    for path in unify(src):
        name = basename(path)
        dst = join(dst_dir, name)
        if isdir(path):
            copytree(path, dst)
        else:
            copy2(path, dst)
