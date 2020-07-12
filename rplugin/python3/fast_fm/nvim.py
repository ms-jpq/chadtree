from __future__ import annotations

from typing import Any, Optional, Sequence

from pynvim import Nvim

Nvim = Nvim
Tabpage = Any
Window = Any
Buffer = Any


def print(nvim: Nvim, message: Any, error: bool = False, flush: bool = True) -> None:
    write = nvim.api.err_write if error else nvim.api.out_write
    write(str(message))
    if flush:
        write("\n")


def find_buffer(nvim: Nvim, bufnr: int) -> Optional[Buffer]:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        if buffer.number == bufnr:
            return buffer
    return None


class HoldPosition:
    def __init__(self, nvim: Nvim, window: Optional[Window] = None):
        self.nvim = nvim
        self.window = window or nvim.api.get_current_win()

    def __enter__(self) -> None:
        pos = self.nvim.api.win_get_cursor(self.window)
        self.pos = pos

    def __exit__(self, *_) -> None:
        row, col = self.pos
        buffer: Buffer = self.nvim.api.win_get_buf(self.window)
        max_rows = self.nvim.api.buf_line_count(buffer)
        r = min(row, max_rows)
        self.nvim.api.win_set_cursor(self.window, (r, col))


class HoldWindowPosition:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    def __enter__(self) -> None:
        self.window = self.nvim.api.get_current_win()

    def __exit__(self, *_) -> None:
        self.nvim.api.set_current_win(self.window)
