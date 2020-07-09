from __future__ import annotations

from dataclasses import dataclass, field
from enum import Flag, auto
from typing import Dict, Iterable, Optional, Set

Selection = Set[str]


class Mode(Flag):
    FILE = auto()
    FOLDER = auto()
    LINK = auto()


@dataclass
class Node:
    path: str
    mode: Mode
    name: str
    children: Optional[Dict[str, Node]] = None
    ext: Optional[str] = None


@dataclass
class Index:
    selection: Selection
    root: Node


@dataclass
class DisplayNode:
    path: str
    mode: Mode
    name: str
    children: Iterable[DisplayNode] = field(default_factory=tuple)
    hidden: bool = False


@dataclass
class DisplayIndex:
    selection: Selection
    root: DisplayNode
