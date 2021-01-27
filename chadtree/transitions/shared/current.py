from os.path import dirname
from typing import AbstractSet, Optional

from pynvim import Nvim
from std2.pathlib import longest_common_path, is_relative_to

from ...fs.cartographer import new
from ...fs.ops import ancestors
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..types import Stage


def new_current_file(
    nvim: Nvim, state: State, settings: Settings, current: str
) -> Optional[Stage]:
    """
    New file focused in buf
    """

    parents = ancestors(current)
    if state.root.path in parents:
        paths: AbstractSet[str] = parents if state.follow else set()
        index = state.index | paths
        new_state = forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return Stage(new_state)
    else:
        return None


def new_root(
    nvim: Nvim,
    state: State,
    settings: Settings,
    new_cwd: str,
    indices: AbstractSet[str],
) -> State:
    index = state.index | ancestors(new_cwd) | {new_cwd} | indices
    root = new(new_cwd, index=index)
    selection = {path for path in state.selection if root.path in ancestors(path)}
    return forward(
        state, settings=settings, root=root, selection=selection, index=index
    )


def maybe_path_above(
    nvim: Nvim, state: State, settings: Settings, path: str
) -> Optional[State]:
    root = state.root.path
    if is_relative_to(path, root):
        return None
    else:
        lcp = longest_common_path(path, root)
        new_cwd = str(lcp) if lcp else dirname(path)
        indices = ancestors(path)
        return new_root(
            nvim, state=state, settings=settings, new_cwd=new_cwd, indices=indices
        )
