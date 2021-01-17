from typing import Optional

from pynvim import Nvim

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import FilterPattern, Selection, State
from .types import Stage


@rpc(blocking=False)
def _clear_filter(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Clear filter
    """

    new_state = forward(state, settings=settings, filter_pattern=None)
    return Stage(new_state)


@rpc(blocking=False)
def _filter(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Update filter
    """

    old_p = state.filter_pattern.pattern if state.filter_pattern else ""
    pattern: Optional[str] = nvim.funcs.input(LANG("new_filter"), old_p)
    filter_pattern = FilterPattern(pattern=pattern) if pattern else None
    selection: Selection = state.selection if filter_pattern else set()
    new_state = forward(
        state, settings=settings, selection=selection, filter_pattern=filter_pattern
    )
    return Stage(new_state)
