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
from pynvim_pp.api import cur_win, win_get_cursor, win_set_cursor


@rpc(blocking=False)
def _collapse(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Collapse folder
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if node:
        path = node.path if is_dir(node) else dirname(node.path)
        if path != state.root.path:
            paths = frozenset(
                indexed
                for indexed in state.index
                if path in (ancestors(indexed) | {indexed})
            )
            index = state.index - paths
            new_state = forward(state, settings=settings, index=index, paths=paths)
            row = new_state.derived.paths_lookup.get(path, 0)
            if row:
                win = cur_win(nvim)
                _, col = win_get_cursor(nvim, win=win)
                win_set_cursor(nvim, win=win, row=row + 1, col=col)

            return Stage(new_state)
        else:
            return None
    else:
        return None
