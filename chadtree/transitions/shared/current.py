from pathlib import PurePath
from typing import AbstractSet, Iterator, Optional

from std2.locale import pathsort_key
from std2.pathlib import is_relative_to, longest_common_path

from ...fs.cartographer import new
from ...fs.ops import ancestors
from ...state.next import forward
from ...state.types import State
from ..types import Stage


async def new_current_file(state: State, current: PurePath) -> Stage:
    """
    New file focused in buf
    """

    parents = ancestors(current)
    if state.root.path in parents:
        invalidate_dirs = {current.parent}
        index = state.index | parents
        new_state = await forward(
            state,
            index=index,
            invalidate_dirs=invalidate_dirs,
            current=current,
        )
    else:
        new_state = await forward(state, current=current)

    focus = current if state.follow else None
    return Stage(new_state, focus=focus)


async def new_root(
    state: State,
    new_cwd: PurePath,
    indices: AbstractSet[PurePath],
) -> State:
    index = state.index | ancestors(new_cwd) | {new_cwd} | indices
    root = await new(
        state.executor, follow_links=state.follow_links, root=new_cwd, index=index
    )
    selection = {path for path in state.selection if root.path in ancestors(path)}
    return await forward(state, root=root, selection=selection, index=index)


async def maybe_path_above(
    state: State, paths: AbstractSet[PurePath]
) -> Optional[State]:
    root = state.root.path
    if all(is_relative_to(path, root) for path in paths):
        return None
    else:

        def cont() -> Iterator[PurePath]:
            for path in paths:
                lcp = longest_common_path(path, root)
                yield lcp if lcp else path.parent

        ordered = sorted(cont(), key=pathsort_key)
        indices = ancestors(*ordered)
        new_cwd, *_ = ordered
        return await new_root(state=state, new_cwd=new_cwd, indices=indices)
