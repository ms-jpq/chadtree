from dataclasses import dataclass
from typing import FrozenSet, Mapping, Optional, Union

from ..view.types import ViewOptions


@dataclass(frozen=True)
class VersionCtlOpts:
    defer: bool
    enable: bool


@dataclass(frozen=True)
class MimetypeOptions:
    warn: FrozenSet[str]
    ignore_exts: FrozenSet[str]


@dataclass(frozen=True)
class UserIgnore:
    name: FrozenSet[str]
    path: FrozenSet[str]


@dataclass(frozen=True)
class Settings:
    follow: bool
    ignores: UserIgnore
    keymap: Mapping[str, FrozenSet[str]]
    lang: Optional[str]
    mime: MimetypeOptions
    open_left: bool
    polling_rate: float
    session: bool
    show_hidden: bool
    version_ctl: VersionCtlOpts
    view: ViewOptions
    width: int
    win_local_opts: Mapping[str, Union[bool, str]]
