from typing import Optional

from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .types import Stage


@rpc(blocking=False, name="CHADclear_filter")
def c_clear_filter(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Clear filter
    """

    new_state = forward(state, settings=settings, filter_pattern=None)
    return Stage(new_state)


@rpc(blocking=False, name="CHADfilter")
def c_new_filter(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Update filter
    """

    old_p = state.filter_pattern.pattern if state.filter_pattern else ""
    pattern: Optional[str] = nvim.funcs.input(LANG("new_filter"), old_p)
    filter_pattern = FilterPattern(pattern=pattern) if pattern else None
    new_state = forward(
        state, settings=settings, selection=frozenset(), filter_pattern=filter_pattern
    )
    return Stage(new_state)
