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

        def f(*args: Any, **kwargs) -> None:
            nonlocal fut
            fn = getattr(self.__attr, name)
            ret = fn(*args, **kwargs)
            fut.set_result(ret)
            fut = Future()

        def run(*args: Any, **kwargs) -> Awaitable[Any]:
            self.__nvim.async_call(f, *args, **kwargs)
            return fut

        return run


class Nvim2:
    def __init__(self, nvim: Nvim):
        self.funcs = Asynced(nvim, "funcs")
        self.api = Asynced(nvim, "api")
        self.command = self.api.command

    async def print(
        self, message: Any, error: bool = False, flush: bool = True
    ) -> None:
        write = self.api.err_write if error else self.api.out_write
        await write(str(message))
        if flush:
            await write("\n")


async def find_buffer(nvim: Nvim2, bufnr: int) -> Optional[Buffer]:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()
    for buffer in buffers:
        if buffer.number == bufnr:
            return buffer
    return None
