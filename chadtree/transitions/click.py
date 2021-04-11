from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import list_wins, win_close
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..fs.types import Mode
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .shared.open_file import open_file
from .shared.wm import find_fm_windows_in_tab
from .types import ClickType, Stage, State


def _click(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool, click_type: ClickType
) -> Optional[Stage]:
    node = next(indices(nvim, state=state, is_visual=is_visual), None)

    if not node:
        return None
    else:
        if Mode.orphan_link in node.mode:
            name = node.name
            write(nvim, LANG("dead_link", name=name), error=True)
            return None
        else:
            if is_dir(node):
                if node.path == state.root.path:
                    return None
                elif state.filter_pattern:
                    write(nvim, LANG("filter_click"))
                    return None
                else:
                    paths = {node.path}
                    index = state.index ^ paths
                    new_state = forward(
                        state, settings=settings, index=index, paths=paths
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

                if settings.close_on_open:
                    wins = list_wins(nvim)
                    if len(wins) <= 1:
                        nvim.api.command("quit")
                    else:
                        for win in find_fm_windows_in_tab(nvim):
                            win_close(nvim, win=win)

                return nxt


@rpc(blocking=False)
def _primary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open
    """

    return _click(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.primary,
    )


@rpc(blocking=False)
def _secondary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> preview
    """

    return _click(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.secondary,
    )


@rpc(blocking=False)
def _tertiary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in new tab
    """

    return _click(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.tertiary,
    )


@rpc(blocking=False)
def _v_split(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in vertical split
    """

    return _click(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.v_split,
    )


@rpc(blocking=False)
def _h_split(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in horizontal split
    """

    return _click(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.h_split,
    )
