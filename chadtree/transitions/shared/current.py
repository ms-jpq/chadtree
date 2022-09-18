from pathlib import PurePath
from typing import AbstractSet, Optional

from std2.pathlib import is_relative_to, longest_common_path

from ...fs.cartographer import new
from ...fs.ops import ancestors
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..types import Stage


async def new_current_file(
    state: State, settings: Settings, current: PurePath
) -> Optional[Stage]:
    """
    New file focused in buf
    """

    parents = ancestors(current)
    if state.root.path in parents:
        index = state.index | parents
        new_state = await forward(
            state, settings=settings, index=index, paths=parents, current=current
        )
        return Stage(new_state)
    else:
        return None


async def new_root(
    state: State,
    settings: Settings,
    new_cwd: PurePath,
    indices: AbstractSet[PurePath],
) -> State:
    index = state.index | ancestors(new_cwd) | {new_cwd} | indices
    root = await new(new_cwd, index=index)
    selection = {path for path in state.selection if root.path in ancestors(path)}
    return await forward(
        state, settings=settings, root=root, selection=selection, index=index
    )


async def maybe_path_above(
    state: State, settings: Settings, path: PurePath
) -> Optional[State]:
    root = state.root.path
    if is_relative_to(path, root):
        return None
    else:
        lcp = longest_common_path(path, root)
        new_cwd = lcp if lcp else path.parent
        indices = ancestors(path)
        return await new_root(
            state=state, settings=settings, new_cwd=new_cwd, indices=indices
        )
