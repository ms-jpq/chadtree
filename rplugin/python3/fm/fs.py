from __future__ import annotations

from os import makedirs
from os import remove as rm
from os.path import dirname, isdir, sep
from pathlib import Path
from shutil import copy2, copytree
from shutil import move as mv
from shutil import rmtree


def new(dest: str, folder_mode: int = 0o755, file_mode: int = 0o644) -> None:
    if dest.endswith(sep):
        makedirs(dest, mode=folder_mode, exist_ok=True)
    else:
        parent = dirname(dest)
        makedirs(parent, mode=folder_mode, exist_ok=True)
        Path(dest).touch(mode=file_mode, exist_ok=True)


def rename(src: str, dest: str) -> None:
    mv(src, dest)


def remove(src: str) -> None:
    if isdir(src):
        rmtree(src)
    else:
        rm(src)


def cut(src: str, dest: str) -> None:
    mv(src, dest)


def copy(src: str, dest: str) -> None:
    if isdir(src):
        copytree(src, dest)
    else:
        copy2(src, dest)
