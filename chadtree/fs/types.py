from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import AbstractSet, Mapping, Optional, Sequence
from pathlib import PurePath


class Mode(IntEnum):
    orphan_link = auto()
    link = auto()
    sticky_writable = auto()
    sticky_dir = auto()
    folder = auto()
    block_device = auto()
    char_device = auto()
    door = auto()
    executable = auto()
    multi_hardlink = auto()
    other_writable = auto()
    pipe = auto()
    set_gid = auto()
    set_uid = auto()
    socket = auto()
    file_w_capacity = auto()
    file = auto()


@dataclass(frozen=True)
class Node:
    mode: AbstractSet[Mode]
    path: PurePath
    ancestors: AbstractSet[PurePath]
    children: Mapping[PurePath, Node] = field(default_factory=dict)


@dataclass(frozen=True)
class Ignored:
    name_exact: AbstractSet[PurePath]
    name_glob: Sequence[str]
    path_glob: Sequence[str]
