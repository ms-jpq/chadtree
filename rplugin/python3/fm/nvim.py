from typing import Any

from pynvim import Nvim

Tabpage = Any
Window = Any
Buffer = Any


def print(nvim: Nvim, message: str, error: bool = False) -> None:
    write = nvim.err_write if error else nvim.out_write
    write(message)
    write("\n")
