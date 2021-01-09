from typing import Optional

from pynvim import Nvim
from pynvim_pp.lib import s_write

from ..fs.types import Mode
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import index
from .shared.open_file import open_file
from .types import ClickType, Stage, State


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
                nxt = open_file(
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
