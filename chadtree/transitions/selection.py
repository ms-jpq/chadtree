from typing import Optional

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

    new_state = forward(state, settings=settings, selection=frozenset())
    return Stage(new_state)


@rpc(blocking=False)
def _select(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folder / File -> select
    """

    nodes = iter(indices(nvim, state=state, is_visual=is_visual))
    if is_visual:
        selection = state.selection ^ {n.path for n in nodes}
        new_state = forward(state, settings=settings, selection=selection)
        return Stage(new_state)
    else:
        node = next(nodes, None)
        if node:
            selection = state.selection ^ {node.path}
            new_state = forward(state, settings=settings, selection=selection)
            return Stage(new_state)
        else:
            return None
