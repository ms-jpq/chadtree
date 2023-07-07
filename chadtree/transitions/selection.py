from ..registry import rpc
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _clear_selection(state: State, is_visual: bool) -> Stage:
    """
    Clear selected
    """

    new_state = await forward(state, selection=frozenset())
    return Stage(new_state)


@rpc(blocking=False)
async def _select(state: State, is_visual: bool) -> Stage:
    """
    Folder / File -> select
    """

    nodes = indices(state, is_visual=is_visual)
    selection = state.selection ^ {node.path async for node in nodes}
    new_state = await forward(state, selection=selection)
    return Stage(new_state)
