from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _clear_selection(state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Clear selected
    """

    new_state = await forward(state, settings=settings, selection=frozenset())
    return Stage(new_state)


@rpc(blocking=False)
async def _select(state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Folder / File -> select
    """

    nodes = indices(state, is_visual=is_visual)
    selection = state.selection ^ {node.path async for node in nodes}
    new_state = await forward(state, settings=settings, selection=selection)
    return Stage(new_state)
