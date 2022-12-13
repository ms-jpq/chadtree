from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto, unique
from pathlib import PurePath
from typing import AbstractSet, Mapping, Sequence


@unique
class Mode(IntEnum):
    multi_hardlink = auto()
    file_w_capacity = auto()
    sticky_writable = auto()
    other_writable = auto()
    sticky_dir = auto()
    set_gid = auto()
    set_uid = auto()
    door = auto()
    executable = auto()
    orphan_link = auto()
    char_device = auto()
    block_device = auto()
    socket = auto()
    pipe = auto()
    link = auto()
    folder = auto()
    file = auto()


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
