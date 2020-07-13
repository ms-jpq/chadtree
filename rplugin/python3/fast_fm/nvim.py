from __future__ import annotations

from asyncio import Future
from typing import Any, Awaitable, Optional, Protocol, Sequence

from pynvim import Nvim

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


async def print(
    nvim: Nvim2, message: Any, error: bool = False, flush: bool = True
) -> None:
    write = nvim.api.err_write if error else nvim.api.out_write
    await write(str(message))
    if flush:
        await write("\n")


async def find_buffer(nvim: Nvim2, bufnr: int) -> Optional[Buffer]:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()
    for buffer in buffers:
        if buffer.number == bufnr:
            return buffer
    return None


class HoldPosition:
    def __init__(self, nvim: Nvim2):
        self.nvim = nvim

    async def __aenter__(self) -> None:
        self.window = await self.nvim.api.get_current_win()
        self.pos = await self.nvim.api.win_get_cursor(self.window)

    async def __aexit__(self, *_) -> None:
        row, col = self.pos
        buffer: Buffer = await self.nvim.api.win_get_buf(self.window)
        max_rows = await self.nvim.api.buf_line_count(buffer)
        r = min(row, max_rows)
        await self.nvim.api.win_set_cursor(self.window, (r, col))


class HoldWindowPosition:
    def __init__(self, nvim: Nvim2):
        self.nvim = nvim

    async def __aenter__(self) -> None:
        self.window = await self.nvim.api.get_current_win()

    async def __aexit__(self, *_) -> None:
        await self.nvim.api.set_current_win(self.window)
