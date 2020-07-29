from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Sequence, Set

Index = Set[str]
Selection = Set[str]


class Mode(Enum):
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
    path: str
    mode: Set[Mode]
    name: str
    children: Optional[Dict[str, Node]] = None
    ext: Optional[str] = None


@dataclass(frozen=True)
class Session:
    index: Index


@dataclass(frozen=True)
class IconSet:
    folder_open: str
    folder_closed: str
    link: str
    link_broken: str
    filetype: Dict[str, str]
    filename: Dict[str, str]
    selected: str
    active: str


@dataclass(frozen=True)
class UpdateTime:
    min_time: float
    max_time: float


@dataclass(frozen=True)
class VersionControlOptions:
    defer: bool


@dataclass(frozen=True)
class Settings:
    show_hidden: bool
    follow: bool
    open_left: bool
    width: int
    keymap: Dict[str, Sequence[str]]
    name_ignore: Sequence[str]
    path_ignore: Sequence[str]
    use_icons: bool
    icons: IconSet
    update: UpdateTime
    version_ctl: VersionControlOptions
    session: bool


@dataclass(frozen=True)
class QuickFix:
    locations: Dict[str, int]


@dataclass(frozen=True)
class VCStatus:
    ignored: Set[str] = field(default_factory=set)
    status: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Highlight:
    begin: int
    end: int
    group: str


@dataclass(frozen=True)
class Badge:
    text: str
    group: str


@dataclass(frozen=True)
class Render:
    line: str
    badges: Sequence[Badge]
    highlights: Sequence[Highlight]


@dataclass(frozen=True)
class State:
    index: Index
    selection: Selection
    show_hidden: bool
    follow: bool
    width: int
    root: Node
    qf: QuickFix
    vc: VCStatus
    current: Optional[str]
    lookup: Sequence[Node]
    rendered: Sequence[Render]
