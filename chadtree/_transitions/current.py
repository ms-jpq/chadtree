from pynvim import Nvim

from ..settings.types import Settings
from ..state.types import State
from ..registry import rpc
from typing import Optional
from .types import Stage
from ..state.next import forward
from typing import FrozenSet



def current(
    nvim: Nvim, state: State, settings: Settings, current: str
) -> Optional[Stage]:
    if is_parent(parent=state.root.path, child=current):
        paths: FrozenSet[str] = (
            frozenset(ancestors(current)) if state.follow else frozenset()
        )
        index = state.index | paths
        new_state = forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return Stage(new_state)
    else:
        return None
