from dataclasses import dataclass
from typing import AbstractSet, Mapping, Optional, Union

from ..fs.types import Ignored
from ..view.types import ViewOptions


@dataclass(frozen=True)
class VersionCtlOpts:
    enable: bool


@dataclass(frozen=True)
class MimetypeOptions:
    warn: AbstractSet[str]
    allow_exts: AbstractSet[str]


@dataclass(frozen=True)
class Settings:
    close_on_open: bool
    follow: bool
    follow_links: bool
    ignores: Ignored
    keymap: Mapping[str, AbstractSet[str]]
    lang: Optional[str]
    mime: MimetypeOptions
    open_left: bool
    page_increment: int
    polling_rate: float
    idle_timeout: float
    profiling: bool
    session: bool
    show_hidden: bool
    version_ctl: VersionCtlOpts
    view: ViewOptions
    width: int
    win_actual_opts: Mapping[str, Union[bool, str]]
    win_local_opts: Mapping[str, Union[bool, str]]
    min_diagnostics_severity: int
    xdg: bool
