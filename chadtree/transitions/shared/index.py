from typing import Iterator, Optional

from pynvim.api import Nvim
from pynvim_pp.api import cur_win, win_get_buf, win_get_cursor
from pynvim_pp.operators import operator_marks

from ...fs.types import Node
from ...state.types import State
from .wm import is_fm_buffer


def _row_index(state: State, row: int) -> Optional[Node]:
    if (row >= 0) and (row < len(state.derived.node_row_lookup)):
        return state.derived.node_row_lookup[row]
    else:
        return None


def indices(nvim: Nvim, state: State, is_visual: bool) -> Iterator[Node]:
    win = cur_win(nvim)
    buf = win_get_buf(nvim, win=win)

    if not is_fm_buffer(nvim, buf=buf):
        return None
    else:
        row, _ = win_get_cursor(nvim, win=win)
        node = _row_index(state, row)
        if node:
            yield node

        if is_visual:
            (row1, _), (row2, _) = operator_marks(nvim, buf=buf, visual_type=None)

            for r in range(row1, row2 + 1):
                if r != row:
                    node = _row_index(state, r)
                    if node:
                        yield node
