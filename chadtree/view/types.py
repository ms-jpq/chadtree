from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping, Optional, Sequence

from pynvim_pp.highlight import HLgroup

from ..fs.types import Mode, Node


class ColourChoice(Enum):
    ls_colours = auto()
    nerd_tree = auto()


@dataclass(frozen=True)
class NerdColours:
    ext_exact: Mapping[str, str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]


@dataclass(frozen=True)
class FolderIcons:
    open: str
    closed: str


@dataclass(frozen=True)
class LinkIcons:
    normal: str
    broken: str


@dataclass(frozen=True)
class StatusIcons:
    active: str
    inactive: str
    selected: str
    not_selected: str


@dataclass(frozen=True)
class Icons:
    ext_exact: Mapping[str, str]
    default_icon: str
    folder: FolderIcons
    link: LinkIcons
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    status: StatusIcons


GithubColours = Mapping[str, str]


@dataclass(frozen=True)
class HLGroups:
    ignored: str
    quickfix: str
    version_control: str


@dataclass(frozen=True)
class HLcontext:
    groups: Sequence[HLgroup]
    icon_exts: GithubColours
    mode_pre: Mapping[Mode, str]
    mode_post: Mapping[Optional[Mode], str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    ext_exact: Mapping[str, str]
    particular_mappings: HLGroups


class Sortby(Enum):
    is_folder = auto()
    ext = auto()
    file_name = auto()


@dataclass(frozen=True)
class ViewOptions:
    hl_context: HLcontext
    icons: Icons
    sort_by: Sequence[Sortby]
    time_fmt: str
    use_icons: bool


@dataclass(frozen=True)
class Badge:
    text: str
    group: str


@dataclass(frozen=True)
class Highlight:
    begin: int
    end: int
    group: str


@dataclass(frozen=True)
class Render:
    badges: Sequence[Badge]
    highlights: Sequence[Highlight]
    line: str


@dataclass(frozen=True)
class Derived:
    rendered: Sequence[Render]
    hashed: Sequence[int]
    node_row_lookup: Sequence[Node]
    path_row_lookup: Mapping[str, int]
