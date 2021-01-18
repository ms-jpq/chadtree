from dataclasses import dataclass
from typing import AbstractSet, Mapping, Optional, Sequence, Union

from ..view.types import ViewOptions


@dataclass(frozen=True)
class VersionCtlOpts:
    enable: bool


@dataclass(frozen=True)
class MimetypeOptions:
    warn: AbstractSet[str]
    ignore_exts: AbstractSet[str]


@dataclass(frozen=True)
class IgnoreOpts:
    name_exact: AbstractSet[str]
    name_glob: Sequence[str]
    path_glob: Sequence[str]


@dataclass(frozen=True)
class Settings:
    follow: bool
    ignores: IgnoreOpts
    page_increment: int
    keymap: Mapping[str, AbstractSet[str]]
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
