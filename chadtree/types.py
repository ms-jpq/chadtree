from __future__ import annotations

from dataclasses import dataclass, field


from typing import FrozenSet, Mapping, Optional

from .fs.types import Node
from .view.types import Derived
from .nvim.types import QuickFix

Index = FrozenSet[str]
Selection = FrozenSet[str]


@dataclass(frozen=True)
class OpenArgs:
    focus: bool


@dataclass(frozen=True)
class FilterPattern:
    pattern: str



@dataclass(frozen=True)
class VCStatus:
    ignored: FrozenSet[str] = frozenset()
    status: Mapping[str, str] = field(default_factory=dict)


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
