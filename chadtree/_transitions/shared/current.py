from typing import FrozenSet, Optional

from pynvim import Nvim

from ..fs.ops import ancestors, is_parent
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .types import Stage


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
