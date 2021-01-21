from operator import add, sub
from typing import Callable, Optional

from pynvim import Nvim
from pynvim_pp.api import cur_win

from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.wm import is_fm_window, resize_fm_windows
from .types import Stage


def _resize(
    nvim: Nvim, state: State, settings: Settings, direction: Callable[[int, int], int]
) -> Optional[Stage]:
    win = cur_win(nvim)
    if not is_fm_window(nvim, win=win):
        return None
    else:
        w_width = win.width
        width = max(direction(w_width, 10), 1)
        new_state = forward(state, settings=settings, width=width)
        resize_fm_windows(nvim, width=new_state.width)
        return Stage(new_state)


@rpc(blocking=False)
def _bigger(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Bigger sidebar
    """

    return _resize(nvim, state=state, settings=settings, direction=add)


@rpc(blocking=False)
def _smaller(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Smaller sidebar
    """

    return _resize(nvim, state=state, settings=settings, direction=sub)
