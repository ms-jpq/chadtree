from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Sequence, Tuple
from webbrowser import open as open_w

from pynvim import Nvim
from pynvim_pp.api import buf_set_lines, buf_set_option, create_buf
from pynvim_pp.float_win import open_float_win
from pynvim_pp.lib import write
from std2.argparse import ArgparseError, ArgParser
from std2.types import never

from ..consts import (
    CONFIGURATION_MD,
    CONFIGURATION_URI,
    FEATURES_MD,
    FEATURES_URI,
    KEYBIND_MD,
    KEYBIND_URI,
    README_MD,
    README_URI,
    THEME_MD,
    THEME_URI,
)
from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State


class _Pages(Enum):
    features = auto()
    keybind = auto()
    config = auto()
    theme = auto()


@dataclass(frozen=True)
class _Args:
    page: Optional[_Pages]
    use_web: bool


def _directory(page: Optional[_Pages]) -> Tuple[Path, str]:
    if page is None:
        return README_MD, README_URI
    elif page is _Pages.features:
        return FEATURES_MD, FEATURES_URI
    elif page is _Pages.keybind:
        return KEYBIND_MD, KEYBIND_URI
    elif page is _Pages.config:
        return CONFIGURATION_MD, CONFIGURATION_URI
    elif page is _Pages.theme:
        return THEME_MD, THEME_URI
    else:
        never(page)


def _parse_args(args: Sequence[str]) -> _Args:
    parser = ArgParser()
    parser.add_argument(
        "page",
        nargs="?",
        choices=tuple(p.name for p in _Pages),
        default=None,
    )
    parser.add_argument("-w", "--web", action="store_true", default=False)
    ns = parser.parse_args(args)
    opts = _Args(page=_Pages[ns.page] if ns.page else None, use_web=ns.web)
    return opts


@rpc(blocking=False)
def _help(nvim: Nvim, state: State, settings: Settings, args: Sequence[str]) -> None:
    """
    Open help doc
    """

    try:
        opts = _parse_args(args)
    except ArgparseError as e:
        write(nvim, e, error=True)
    else:
        md, uri = _directory(opts.page)
        if opts.use_web:
            open_w(uri)
        else:
            lines = md.read_text().splitlines()
            buf = create_buf(nvim, listed=False, scratch=True, wipe=True, nofile=True)
            buf_set_lines(nvim, buf=buf, lo=0, hi=-1, lines=lines)
            buf_set_option(nvim, buf=buf, key="modifiable", val=False)
            buf_set_option(nvim, buf=buf, key="filetype", val="markdown")
            open_float_win(nvim, margin=0, relsize=0.95, buf=buf)
