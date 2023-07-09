from asyncio import (
    AbstractEventLoop,
    Future,
    get_running_loop,
    run,
    run_coroutine_threadsafe,
    wrap_future,
)
from concurrent.futures import Future as TFuture
from threading import Thread
from typing import Awaitable, Optional, TypeVar

from std2.asyncio import cancel

_T = TypeVar("_T")


class CurrentExecutor:
    def __init__(self) -> None:
        self._ready: TFuture = TFuture()
        self._rdy = wrap_future(self._ready)
        self._loop: Optional[AbstractEventLoop] = None
        self._fut: Optional[Future] = None

        async def cont() -> None:
            self._loop = get_running_loop()
            self._ready.set_result(None)
            await self._loop.create_future()

        self._th = Thread(daemon=True, target=lambda: run(cont()))
        self._th.start()

    async def run(self, co: Awaitable[_T]) -> _T:
        await self._rdy
        assert self._loop
        if self._fut:

            async def cont() -> None:
                assert self._fut
                await cancel(self._fut)

            die = run_coroutine_threadsafe(cont(), loop=self._loop)
            await wrap_future(die)

        fut = run_coroutine_threadsafe(co, loop=self._loop)
        self._fut = wrapped = wrap_future(fut)
        return await wrapped
