from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping, Optional, Sequence

from pynvim_pp.highlight import HLgroup

from ..fs.types import Mode, Node


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
    selected: str


@dataclass(frozen=True)
class UserIcons:
    default_icon: str
    folder: UserFolderIcons
    link: UserLinkIcons
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    status: UserStatusIcons
    type: Mapping[str, str]


@dataclass(frozen=True)
class UserColourMapping:
    hl8: str
    hl24: str


@dataclass(frozen=True)
class UserHLGroups:
    quickfix: str
    version_control: str


@dataclass(frozen=True)
class UserHighlights:
    eight_bit: Mapping[str, UserColourMapping]
    exts: Mapping[str, HLgroup]
    groups: UserHLGroups


@dataclass(frozen=True)
class HLcontext:
    ext_lookup: Mapping[str, HLgroup]
    groups: Sequence[HLgroup]
    mode_lookup_post: Mapping[Optional[Mode], HLgroup]
    mode_lookup_pre: Mapping[Mode, HLgroup]
    name_lookup: Mapping[str, HLgroup]


class Sortby(Enum):
    is_folder = auto()
    ext = auto()
    fname = auto()


@dataclass(frozen=True)
class ViewOptions:
    highlights: UserHighlights
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