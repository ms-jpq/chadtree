from __future__ import annotations

from dataclasses import dataclass, field
from enum import Flag, auto
from typing import Dict, Optional, Sequence, Set

Index = Set[str]
Selection = Set[str]


class Mode(Flag):
    FILE = auto()
    FOLDER = auto()
    LINK = auto()


@dataclass(frozen=True)
class Node:
    path: str
    mode: Mode
    name: str
    children: Optional[Dict[str, Node]] = None
    ext: Optional[str] = None


@dataclass(frozen=True)
class Settings:
    width: int
    keymap: Dict[str, Sequence[str]]
    ignored: Set[str]
    icons: Dict[str, str]


@dataclass(frozen=True)
class GitStatus:
    ignored: Set[str] = field(default_factory=set)
    modified: Set[str] = field(default_factory=set)
    staged: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class State:
    index: Index
    selection: Selection
    root: Node
    rendered: Sequence[str]
    path_lookup: Sequence[str]
