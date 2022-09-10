from operator import add, sub
from typing import Callable, Optional

from pynvim_pp.window import Window

from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.wm import is_fm_window, resize_fm_windows
from .types import Stage


async def _resize(
    state: State, settings: Settings, direction: Callable[[int, int], int]
) -> Optional[Stage]:
    win = await Window.get_current()
    if not await is_fm_window(win):
        return None
    else:
        old_width = await win.get_width()
        new_width = max(direction(old_width, 10), 1)
        new_state = await forward(state, settings=settings, width=new_width)
        await resize_fm_windows(new_state.window_order, width=new_state.width)
        return Stage(new_state)


@rpc(blocking=False)
async def _bigger(state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    Bigger sidebar
    """

    return await _resize(state, settings=settings, direction=add)


@rpc(blocking=False)
async def _smaller(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Smaller sidebar
    """

    return await _resize(state, settings=settings, direction=sub)
