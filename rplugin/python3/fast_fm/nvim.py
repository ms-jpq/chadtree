from __future__ import annotations

from asyncio import Future
from typing import Any, Awaitable, Optional, Protocol, Sequence

from pynvim import Nvim

from .da import AnyCallable

Tabpage = Any
Window = Any
Buffer = Any


class AsyncedCallable(Protocol):
    def __call__(self, *args: Any) -> Awaitable[Any]:
        pass


class Asynced:
    def __init__(self, nvim: Nvim, attr: str):
        self.__nvim = nvim
        self.__attr = getattr(nvim, attr)

    def __getattr__(self, name: str) -> AsyncedCallable:
        fut: Future = Future()
        fn = getattr(self.__attr, name)

        def f(*args: Any, **kwargs: Any) -> None:
            nonlocal fut
            ret = fn(*args, **kwargs)
            fut.set_result(ret)
            fut = Future()

        def run(*args: Any) -> Awaitable[Any]:
            self.__nvim.async_call(f, *args)
            return fut

        return run


class Nvim2:
    def __init__(self, nvim: Nvim):
        self._nvim = nvim
        self.funcs = Asynced(nvim, "funcs")
        self.api = Asynced(nvim, "api")
        self.command = self.api.command

    def async_call(self, fn: AnyCallable, *args: Any, **kwargs: Any) -> Awaitable[Any]:
        fut: Future = Future()

        def f(*args: Any, **kwargs) -> None:
            try:
                ret = fn(*args, **kwargs)
            except Exception as e:
                fut.set_exception(e)
            else:
                fut.set_result(ret)

        self._nvim.async_call(f, *args, **kwargs)
        return fut


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


# async def find_buffer(nvim: Nvim2, bufnr: int) -> Optional[Buffer]:
#     buffers: Sequence[Buffer] = await nvim.api.list_bufs()

#     def cont() -> Sequence[Buffer]:
#         for buffer in buffers:
#             if buffer.number == bufnr:
#                 return buffer
#         return None

#     return await nvim.async_call(cont)


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
