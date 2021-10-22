from concurrent.futures import Executor
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet, Optional

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
class State:
    pool: Executor
    session_store: Path
    current: Optional[PurePath]
    derived: Derived
    enable_vc: bool
    filter_pattern: Optional[FilterPattern]
    follow: bool
    index: Index
    qf: Markers
    root: Node
    selection: Selection
    show_hidden: bool
    vc: VCStatus
    width: int


@dataclass(frozen=True)
class Session:
    index: Optional[Index]
    show_hidden: Optional[bool]
    enable_vc: Optional[bool]
