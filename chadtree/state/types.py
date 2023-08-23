from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import AbstractSet, Mapping, Optional

from pynvim_pp.rpc_types import ExtData

from ..fs.types import Node
from ..nvim.types import Markers
from ..settings.types import Settings
from ..version_ctl.types import VCStatus
from ..view.types import Derived
from .executor import CurrentExecutor

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
    executor: CurrentExecutor
    settings: Settings
    session: Session
    follow_links: bool
    vim_focus: bool
    current: Optional[PurePath]
    enable_vc: bool
    filter_pattern: Optional[FilterPattern]
    follow: bool
    index: Index
    markers: Markers
    root: Node
    selection: Selection
    show_hidden: bool
    vc: VCStatus
    width: int
    window_order: Mapping[ExtData, None]

    @property
    def derived(self) -> Derived:
        raise NotImplementedError()


@dataclass(frozen=True)
class StoredSession:
    # TODO: sync across sessions
    # pid: int
    index: Index
    show_hidden: Optional[bool]
    enable_vc: Optional[bool]
