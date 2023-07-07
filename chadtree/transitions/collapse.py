from typing import Optional

from std2 import anext

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors
from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _collapse(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Collapse folder
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        if is_dir(node):
            path = node.path if node.path in state.index else node.path.parent
        else:
            path = node.path.parent

        paths = {
            indexed
            for indexed in state.index
            if path in (ancestors(indexed) | {indexed})
        }

        index = (state.index - paths) | {state.root.path}
        invalidate_dirs = {path}
        new_state = await forward(
            state, settings=settings, index=index, invalidate_dirs=invalidate_dirs
        )
        return Stage(new_state, focus=path)
