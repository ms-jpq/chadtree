from typing import Iterator, Optional

from pynvim.api import Buffer, Nvim, Window

from ...fs.types import Node
from ...state.types import State
from .wm import is_fm_buffer


def _row_index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.derived.lookup)):
        return state.derived.lookup[row]
    else:
        return None


def indices(nvim: Nvim, state: State, is_visual: bool) -> Iterator[Node]:
    window: Window = nvim.api.get_current_win()
    buffer: Buffer = nvim.api.win_get_buf(window)

    if not is_fm_buffer(nvim, buffer=buffer):
        return None
    else:
        row, _ = nvim.api.win_get_cursor(window)
        row = row - 1
        node = _row_index(state, row)
        if node:
            yield node

        if is_visual:
            buffer: Buffer = nvim.api.get_current_buf()
            row1, _ = nvim.api.buf_get_mark(buffer, "<")
            row2, _ = nvim.api.buf_get_mark(buffer, ">")

            for r in range(row1 - 1, row2):
                if r != row:
                    node = _row_index(state, r)
                    if node:
                        yield node