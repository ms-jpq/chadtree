from __future__ import annotations

from asyncio import Future
from typing import Any, Awaitable, Protocol

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
        fn = getattr(self.__attr, name)
        fut: Future = Future()

        def f(*args: Any, **kwargs) -> None:
            try:
                ret = fn(*args, **kwargs)
            except Exception as e:
                fut.set_exception(e)
                raise
            else:
                fut.set_result(ret)

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
            await self.print("\n", error=error, flush=False)
