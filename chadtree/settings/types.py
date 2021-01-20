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
    follow: bool
    ignores: Ignored
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
