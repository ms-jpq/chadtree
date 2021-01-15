from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, auto
from typing import AbstractSet, Mapping, Optional




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
    name: str
    path: str
    children: Optional[Mapping[str, Node]] = None
    ext: Optional[str] = None
