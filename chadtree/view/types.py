from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping, Optional, Sequence

from pynvim_pp.highlight import HLgroup

from ..fs.types import Mode, Node


@dataclass(frozen=True)
class NerdColours:
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    type: Mapping[str, str]


@dataclass(frozen=True)
class UserFolderIcons:
    open: str
    closed: str


@dataclass(frozen=True)
class UserLinkIcons:
    normal: str
    broken: str


@dataclass(frozen=True)
class UserStatusIcons:
    active: str
    inactive: str
    selected: str
    not_selected: str


@dataclass(frozen=True)
class UserIcons:
    default_icon: str
    folder: UserFolderIcons
    link: UserLinkIcons
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    status: UserStatusIcons
    type: Mapping[str, str]


GithubColours = Mapping[str, str]


@dataclass(frozen=True)
class UserHLGroups:
    ignored: str
    quickfix: str
    version_control: str


@dataclass(frozen=True)
class HLcontext:
    groups: Sequence[HLgroup]
    github_exts: Mapping[str, str]
    mode_pre: Mapping[Mode, str]
    mode_post: Mapping[Optional[Mode], str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    ext_exact: Mapping[str, str]
    particular_mappings: UserHLGroups


class Sortby(Enum):
    is_folder = auto()
    ext = auto()
    fname = auto()


@dataclass(frozen=True)
class ViewOptions:
    hl_context: HLcontext
    icons: UserIcons
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
    lookup: Sequence[Node]
    paths_lookup: Mapping[str, int]
    rendered: Sequence[Render]
