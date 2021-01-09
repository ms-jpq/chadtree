from enum import Enum, auto
from mimetypes import guess_type
from os import linesep
from os.path import basename, splitext
from typing import Optional

from pynvim import Nvim
from pynvim_pp.lib import s_write

from ..fs.types import Mode
from ..nvim.wm import show_file
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import index
from ..state.types import State
from .types import Stage, State


class ClickType(Enum):
    primary = auto()
    secondary = auto()
    tertiary = auto()
    v_split = auto()
    h_split = auto()


def _open_file(
    nvim: Nvim, state: State, settings: Settings, path: str, click_type: ClickType
) -> Optional[Stage]:
    name = basename(path)
    _, ext = splitext(name)
    mime, _ = guess_type(name, strict=False)
    m_type, _, _ = (mime or "").partition("/")

    def ask() -> bool:
        question = LANG("mime_warn", name=name, mime=str(mime))
        resp: int = nvim.funcs.confirm(question, LANG("ask_yesno", linesep=linesep), 2)
        return resp == 1

    ans = (
        ask()
        if m_type in settings.mime.warn and ext not in settings.mime.ignore_exts
        else True
    )
    if ans:
        new_state = forward(state, settings=settings, current=path)
        show_file(nvim, state=new_state, settings=settings, click_type=click_type)
        return Stage(new_state)
    else:
        return None


def _click(
    nvim: Nvim, state: State, settings: Settings, click_type: ClickType
) -> Optional[Stage]:
    node = index(nvim, state=state)

    if node:
        if Mode.orphan_link in node.mode:
            name = node.name
            s_write(nvim, LANG("dead_link", name=name), error=True)
            return None
        else:
            if Mode.folder in node.mode:
                if state.filter_pattern:
                    s_write(nvim, LANG("filter_click"))
                    return None
                else:
                    paths = frozenset((node.path,))
                    _index = state.index ^ paths
                    new_state = forward(
                        state, settings=settings, index=_index, paths=paths
                    )
                    return Stage(new_state)
            else:
                nxt = _open_file(
                    nvim,
                    state=state,
                    settings=settings,
                    path=node.path,
                    click_type=click_type,
                )
                return nxt
    else:
        return None


@rpc(blocking=False)
def _primary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.primary)


@rpc(blocking=False)
def _secondary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> preview
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.secondary)


@rpc(blocking=False)
def _tertiary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in new tab
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.tertiary)


@rpc(blocking=False)
def _v_split(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in vertical split
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.v_split)


@rpc(blocking=False)
def _h_split(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in horizontal split
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.h_split)
