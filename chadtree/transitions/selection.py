from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from .shared.index import indices
from ..state.types import State
from .types import Stage


@rpc(blocking=False)
def _clear_selection(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Clear selected
    """

    new_state = forward(state, settings=settings, selection=set())
    return Stage(new_state)


@rpc(blocking=False)
def _select(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Folder / File -> select
    """

    nodes = indices(nvim, state=state, is_visual=is_visual)
    selection = state.selection ^ {node.path for node in nodes}
    new_state = forward(state, settings=settings, selection=selection)
    return Stage(new_state)
