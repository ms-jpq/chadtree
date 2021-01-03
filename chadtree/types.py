from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Mapping, Optional, Sequence, Set

from pynvim_pp.highlight import HLgroup

Index = Set[str]
Selection = Set[str]


@dataclass(frozen=True)
class OpenArgs:
    focus: bool


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
    children: Optional[Mapping[str, Node]] = None
    ext: Optional[str] = None


@dataclass(frozen=True)
class Session:
    index: Index
    show_hidden: bool





@dataclass(frozen=True)
class ColourMapping:
    hl8: str
    hl24: str


@dataclass(frozen=True)
class Colours:
    bit8_mapping: Mapping[str, ColourMapping]
    exts: Mapping[str, HLgroup]


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
    filename_exact: Mapping[str, str]
    filename_glob: Mapping[str, str]
    filetype: Mapping[str, str]
    colours: Colours


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
    mode_lookup_pre: Mapping[Mode, HLgroup]
    mode_lookup_post: Mapping[Optional[Mode], HLgroup]
    ext_lookup: Mapping[str, HLgroup]
    name_lookup: Mapping[str, HLgroup]


class Sortby(Enum):
    is_folder = auto()
    ext = auto()
    fname = auto()


@dataclass(frozen=True)
class Settings:
    follow: bool
    hl_context: HLcontext
    icons: ViewOptions
    keymap: Mapping[str, Sequence[str]]
    lang: Optional[str]
    logging_level: str
    mime: MimetypeOptions
    name_ignore: Sequence[str]
    open_left: bool
    path_ignore: Sequence[str]
    session: bool
    show_hidden: bool
    sort_by: Sequence[Sortby]
    update: UpdateTime
    use_icons: bool
    version_ctl: VersionControlOptions
    width: int
    win_local_opts: Sequence[str]


@dataclass(frozen=True)
class QuickFix:
    locations: Mapping[str, int]


@dataclass(frozen=True)
class VCStatus:
    ignored: Set[str] = field(default_factory=set)
    status: Mapping[str, str] = field(default_factory=dict)


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
    paths_lookup: Mapping[str, int]
    rendered: Sequence[Render]


@dataclass(frozen=True)
class Stage:
    state: State
    focus: Optional[str] = None


class ClickType(Enum):
    primary = auto()
    secondary = auto()
    tertiary = auto()
    v_split = auto()
    h_split = auto()
