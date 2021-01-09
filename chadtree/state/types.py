from dataclasses import dataclass
from typing import FrozenSet, Optional

from ..fs.types import Index, Node
from ..nvim.types import QuickFix
from ..version_ctl.types import VCStatus
from ..view.types import Derived

Selection = FrozenSet[str]


@dataclass(frozen=True)
class FilterPattern:
    pattern: str


@dataclass(frozen=True)
class State:
    current: Optional[str]
    derived: Derived
    enable_vc: bool
    filter_pattern: Optional[FilterPattern]
    follow: bool
    index: Index
    qf: QuickFix
    root: Node
    selection: Selection
    show_hidden: bool
    vc: VCStatus
    width: int


@dataclass(frozen=True)
class Stage:
    state: State
    focus: Optional[str] = None
