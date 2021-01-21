from dataclasses import dataclass
from enum import Enum, auto
from typing import Mapping, Optional, Sequence

from chad_types import IconGlyphs
from pynvim_pp.highlight import HLgroup

from ..fs.types import Mode, Node


@dataclass(frozen=True)
class HLGroups:
    ignored: str
    quickfix: str
    version_control: str


@dataclass(frozen=True)
class HLcontext:
    groups: Sequence[HLgroup]
    icon_exts: Mapping[str, str]
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
    icons: IconGlyphs
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
class Derived:
    lines: Sequence[str]
    highlights: Sequence[Sequence[Highlight]]
    badges: Sequence[Sequence[Badge]]

    hashed: Sequence[str]
    node_row_lookup: Sequence[Node]
    path_row_lookup: Mapping[str, int]
