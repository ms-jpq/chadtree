from pathlib import PurePath
from typing import AbstractSet, Optional

from pynvim import Nvim
from std2.pathlib import is_relative_to, longest_common_path

from ...fs.cartographer import new
from ...fs.ops import ancestors
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..types import Stage


def new_current_file(
    nvim: Nvim, state: State, settings: Settings, current: PurePath
) -> Optional[Stage]:
    """
    New file focused in buf
    """

    parents = ancestors(current)
    if state.root.path in parents:
        paths: AbstractSet[PurePath] = parents if state.follow else set()
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
    new_cwd: PurePath,
    indices: AbstractSet[PurePath],
) -> State:
    index = state.index | ancestors(new_cwd) | {new_cwd} | indices
    root = new(state.pool, root=new_cwd, index=index)
    selection = {path for path in state.selection if root.path in ancestors(path)}
    return forward(
        state, settings=settings, root=root, selection=selection, index=index
    )


def maybe_path_above(
    nvim: Nvim, state: State, settings: Settings, path: PurePath
) -> Optional[State]:
    root = state.root.path
    if is_relative_to(path, root):
        return None
    else:
        lcp = longest_common_path(path, root)
        new_cwd = lcp if lcp else path.parent
        indices = ancestors(path)
        return new_root(
            nvim, state=state, settings=settings, new_cwd=new_cwd, indices=indices
        )
