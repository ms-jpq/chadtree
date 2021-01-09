from typing import Iterator, Optional, Sequence

from pynvim.api import Buffer, Nvim, Window

from ...fs.types import Node
from ...state.types import State
from .wm import is_fm_buffer


def _row_index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.derived.lookup)):
        return state.derived.lookup[row]
    else:
        return None


def index(nvim: Nvim, state: State) -> Optional[Node]:
    window: Window = nvim.api.get_current_win()
    buffer: Buffer = nvim.api.win_get_buf(window)
    if is_fm_buffer(nvim, buffer=buffer):
        row, _ = nvim.api.win_get_cursor(window)
        row = row - 1
        return _row_index(state, row)
    else:
        return None


def indices(nvim: Nvim, state: State, is_visual: bool) -> Sequence[Node]:
    def step() -> Iterator[Node]:
        if is_visual:
            buffer: Buffer = nvim.api.get_current_buf()
            r1, _ = nvim.api.buf_get_mark(buffer, "<")
            r2, _ = nvim.api.buf_get_mark(buffer, ">")
            for row in range(r1 - 1, r2):
                node = _row_index(state, row)
                if node:
                    yield node
        else:
            window: Window = nvim.api.get_current_win()
            row, _ = nvim.api.win_get_cursor(window)
            row = row - 1
            node = _row_index(state, row)
            if node:
                yield node

    return tuple(step())
