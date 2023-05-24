from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet, Mapping, Optional

from pynvim_pp.types import ExtData

from ..fs.types import Node
from ..nvim.types import Markers
from ..version_ctl.types import VCStatus
from ..view.types import Derived

Index = AbstractSet[PurePath]
Selection = Index


@dataclass(frozen=True)
class FilterPattern:
    pattern: str


@dataclass(frozen=True)
class Session:
    workdir: PurePath
    storage: Path


@dataclass(frozen=True)
class State:
    session: Session
    current: Optional[PurePath]
    derived: Derived
    enable_vc: bool
    filter_pattern: Optional[FilterPattern]
    follow: bool
    index: Index
    markers: Markers
    root: Node
    bookmarks: Mapping[int, PurePath]
    selection: Selection
    show_hidden: bool
    vc: VCStatus
    width: int
    window_order: Mapping[ExtData, None]


@dataclass(frozen=True)
class StoredSession:
    index: Index
    bookmarks: Mapping[int, PurePath]
    show_hidden: Optional[bool]
    enable_vc: Optional[bool]
