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
    keymap: Dict[str, str]
    ignored: Sequence[str]


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
    ignore_filter: Set[str]
    git: GitStatus
    rendered: Sequence[str]
    path_lookup: Sequence[str]
