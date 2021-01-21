from os.path import dirname
from typing import Optional

from pynvim import Nvim

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors
from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
def _collapse(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    Collapse folder
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        path = node.path if is_dir(node) else dirname(node.path)
        paths = {
            indexed
            for indexed in state.index
            if path in (ancestors(indexed) | {indexed})
        }
        index = (state.index - paths) | {state.root.path}
        new_state = forward(state, settings=settings, index=index, paths=paths)
        return Stage(new_state, focus=path)
