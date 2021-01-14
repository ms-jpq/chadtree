from typing import AbstractSet, Optional

from pynvim import Nvim

from ...fs.cartographer import new
from ...fs.ops import ancestors
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..types import Stage


def current(
    nvim: Nvim, state: State, settings: Settings, current: str
) -> Optional[Stage]:
    """
    New file focused in buf
    """

    parents = ancestors(current)
    if state.root.path in parents:
        paths: AbstractSet[str] = parents if state.follow else frozenset()
        index = state.index | paths
        new_state = forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return Stage(new_state)
    else:
        return None


def new_cwd(nvim: Nvim, state: State, settings: Settings, new_cwd: str) -> Stage:
    index = state.index | {new_cwd}
    root = new(new_cwd, index=index)
    new_state = forward(state, settings=settings, root=root, index=index)
    return Stage(new_state)
