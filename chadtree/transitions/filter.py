from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import FilterPattern, Selection, State
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _clear_filter(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Clear filter
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        focus = node.path
        new_state = await forward(state, settings=settings, filter_pattern=None)
        return Stage(new_state, focus=focus)


@rpc(blocking=False)
async def _filter(state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    Update filter
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        focus = node.path
        old_p = state.filter_pattern.pattern if state.filter_pattern else ""
        pattern = await Nvim.input(question=LANG("new_filter"), default=old_p)

        filter_pattern = FilterPattern(pattern=pattern) if pattern else None
        selection: Selection = state.selection if filter_pattern else set()
        new_state = await forward(
            state, settings=settings, selection=selection, filter_pattern=filter_pattern
        )
        return Stage(new_state, focus=focus)
