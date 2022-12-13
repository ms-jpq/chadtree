from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto, unique
from pathlib import PurePath
from typing import AbstractSet, Mapping, Sequence


@unique
class Mode(IntEnum):
    file = auto()
    folder = auto()
    link = auto()
    pipe = auto()
    socket = auto()
    block_device = auto()
    char_device = auto()
    orphan_link = auto()
    executable = auto()
    door = auto()
    set_uid = auto()
    set_gid = auto()
    sticky_dir = auto()
    other_writable = auto()
    sticky_writable = auto()
    file_w_capacity = auto()
    multi_hardlink = auto()


@dataclass(frozen=True)
class Node:
    mode: AbstractSet[Mode]
    path: PurePath
    ancestors: AbstractSet[PurePath]
    children: Mapping[PurePath, Node] = field(default_factory=dict)


@dataclass(frozen=True)
class Ignored:
    name_exact: AbstractSet[str]
    name_glob: Sequence[str]
    path_glob: Sequence[str]
