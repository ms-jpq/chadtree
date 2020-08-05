from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Dict, Optional, Sequence, Set

Index = Set[str]
Selection = Set[str]


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
    path: str
    mode: Set[Mode]
    name: str
    children: Optional[Dict[str, Node]] = None
    ext: Optional[str] = None


@dataclass(frozen=True)
class Session:
    index: Index


@dataclass(frozen=True)
class HLgroup:
    name: str
    cterm: Set[str] = field(default_factory=set)
    ctermfg: Optional[str] = None
    ctermbg: Optional[str] = None
    guifg: Optional[str] = None
    guibg: Optional[str] = None


@dataclass(frozen=True)
class ViewOptions:
    time_fmt: str
    active: str
    default_icon: str
    folder_closed: str
    folder_open: str
    link: str
    link_broken: str
    selected: str
    quickfix_hl: str
    version_ctl_hl: str
    ext_colours: Dict[str, HLgroup]
    filename_exact: Dict[str, str]
    filename_glob: Dict[str, str]
    filetype: Dict[str, str]


@dataclass(frozen=True)
class UpdateTime:
    min_time: float
    max_time: float


@dataclass(frozen=True)
class VersionControlOptions:
    defer: bool
    enable: bool


@dataclass(frozen=True)
class MimetypeOptions:
    warn: Set[str]
    ignore_exts: Set[str]


@dataclass(frozen=True)
class HLcontext:
    groups: Sequence[HLgroup]
    mode_lookup_pre: Dict[Mode, HLgroup]
    mode_lookup_post: Dict[Optional[Mode], HLgroup]
    ext_lookup: Dict[str, HLgroup]
    name_lookup: Dict[str, HLgroup]


@dataclass(frozen=True)
class Settings:
    follow: bool
    hl_context: HLcontext
    icons: ViewOptions
    keymap: Dict[str, Sequence[str]]
    name_ignore: Sequence[str]
    open_left: bool
    path_ignore: Sequence[str]
    session: bool
    show_hidden: bool
    update: UpdateTime
    use_icons: bool
    version_ctl: VersionControlOptions
    mime: MimetypeOptions
    width: int


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
class FilterPattern:
    pattern: str


@dataclass(frozen=True)
class State:
    index: Index
    selection: Selection
    filter_pattern: Optional[FilterPattern]
    show_hidden: bool
    follow: bool
    enable_vc: bool
    width: int
    root: Node
    qf: QuickFix
    vc: VCStatus
    current: Optional[str]
    lookup: Sequence[Node]
    paths_lookup: Dict[str, int]
    rendered: Sequence[Render]


class ClickType(Enum):
    primary = auto()
    secondary = auto()
    tertiary = auto()
    v_split = auto()
    h_split = auto()
