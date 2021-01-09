from os.path import dirname
from typing import Optional

from pynvim import Nvim
from pynvim.api import Window

from ..fs.cartographer import is_dir
from ..fs.ops import is_parent
from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import index
from ..state.types import State
from .types import Stage


@rpc(blocking=False)
def _collapse(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Collapse folder
    """

    node = index(nvim, state=state)
    if node:
        path = node.path if is_dir(node) else dirname(node.path)
        if path != state.root.path:
            paths = frozenset(
                i for i in state.index if i == path or is_parent(parent=path, child=i)
            )
            _index = state.index - paths
            new_state = forward(state, settings=settings, index=_index, paths=paths)
            row = new_state.derived.paths_lookup.get(path, 0)
            if row:
                window: Window = nvim.api.get_current_win()
                _, col = nvim.api.win_get_cursor(window)
                nvim.api.win_set_cursor(window, (row + 1, col))

            return Stage(new_state)
        else:
            return None
    else:
        return None
