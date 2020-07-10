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
    name_ignore: Sequence[str]
    path_ignore: Sequence[str]
    use_icons: bool


@dataclass(frozen=True)
class State:
    index: Index
    selection: Selection
    root: Node
    path_lookup: Sequence[str]
    rendered: Sequence[str]


@dataclass(frozen=True)
class GitStatus:
    ignored: Set[str] = field(default_factory=set)
    added: Set[str] = field(default_factory=set)
    modified: Set[str] = field(default_factory=set)
    staged: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class IconSet:
    folder: str
    link: str
    git_ignored: str
    git_modified: str
    git_staged: str
    filetype: Dict[str, str]
