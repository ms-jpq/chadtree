from typing import AsyncIterator, Optional

from pynvim_pp.operators import operator_marks
from pynvim_pp.window import Window

from ...fs.types import Node
from ...state.types import State
from .wm import is_fm_buffer


def _row_index(state: State, row: int) -> Optional[Node]:
    if (row >= 0) and (row < len(state.derived.node_row_lookup)):
        return state.derived.node_row_lookup[row]
    else:
        return None


async def indices(state: State, is_visual: bool) -> AsyncIterator[Node]:
    win = await Window.get_current()
    buf = await win.get_buf()

    if not await is_fm_buffer(buf):
        return
    else:
        row, _ = await win.get_cursor()
        if node := _row_index(state, row):
            yield node

        if is_visual:
            (row1, _), (row2, _) = await operator_marks(buf, visual_type=None)

            for r in range(row1, row2 + 1):
                if r != row:
                    if node := _row_index(state, r):
                        yield node
