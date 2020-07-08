from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, IntEnum, auto
from typing import Iterable, Optional, Set, Union

Selection = Set[str]


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


@dataclass
class Index:
    index: Set[str]
    root: Dir


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


class Highlight(Flag):
    FILE = auto()
    FOLDER = auto()
    LINK = auto()


@dataclass
class DisplayNode:
    original: Node
    name: str
    children: Iterable[DisplayNode]
    highlight: Highlight


@dataclass
class DisplayIndex:
    index: Set[str]
    root: DisplayNode
