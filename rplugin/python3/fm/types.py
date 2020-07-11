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
class GitIcons:
    ignored: str
    added: str
    modified: str
    staged: str


@dataclass(frozen=True)
class IconSet:
    folder: str
    link: str
    git: GitIcons
    filetype: Dict[str, str]


@dataclass(frozen=True)
class Settings:
    width: int
    keymap: Dict[str, Sequence[str]]
    show_hidden: bool
    name_ignore: Sequence[str]
    path_ignore: Sequence[str]
    use_icons: bool
    icons: IconSet


@dataclass(frozen=True)
class Nub:
    path: str
    mode: Mode


@dataclass(frozen=True)
class GitStatus:
    ignored: Set[str] = field(default_factory=set)
    added: Set[str] = field(default_factory=set)
    modified: Set[str] = field(default_factory=set)
    staged: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class State:
    index: Index
    selection: Selection
    show_hidden: bool
    root: Node
    path_lookup: Sequence[str]
    rendered: Sequence[str]
    git: GitStatus
