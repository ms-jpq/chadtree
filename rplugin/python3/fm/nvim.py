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
