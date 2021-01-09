from operator import add, sub
from typing import Callable

from pynvim import Nvim

from ..nvim.wm import resize_fm_windows
from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .types import Stage


def _resize(
    nvim: Nvim, state: State, settings: Settings, direction: Callable[[int, int], int]
) -> Stage:
    width = max(direction(state.width, 10), 1)
    new_state = forward(state, settings=settings, width=width)

    resize_fm_windows(nvim, width=new_state.width)
    return Stage(new_state)


@rpc(blocking=False, name="CHADbigger")
def c_bigger(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Bigger sidebar
    """
    return _resize(nvim, state=state, settings=settings, direction=add)


@rpc(blocking=False, name="CHADsmaller")
def c_smaller(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Smaller sidebar
    """
    return _resize(nvim, state=state, settings=settings, direction=sub)
