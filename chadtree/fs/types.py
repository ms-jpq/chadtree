from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto, unique
from pathlib import PurePath
from typing import AbstractSet, Mapping, Optional, Sequence


# https://github.com/coreutils/coreutils/blob/master/src/ls.c
@unique
class Mode(IntEnum):
    orphan_link = auto()
    link = auto()

    pipe = auto()
    socket = auto()
    block_device = auto()
    char_device = auto()
    door = auto()

    sticky_other_writable = auto()
    other_writable = auto()
    sticky = auto()
    folder = auto()

    set_uid = auto()
    set_gid = auto()
    file_w_capacity = auto()
    executable = auto()
    multi_hardlink = auto()
    file = auto()


@dataclass(frozen=True)
class Node:
    mode: AbstractSet[Mode]
    path: PurePath
    pointed: Optional[PurePath]
    ancestors: AbstractSet[PurePath]
    children: Mapping[PurePath, Node]


@dataclass(frozen=True)
class Ignored:
    name_exact: AbstractSet[str]
    name_glob: Sequence[str]
    path_glob: Sequence[str]
