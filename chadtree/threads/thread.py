from __future__ import annotations

from abc import abstractmethod
from asyncio import (
    AbstractEventLoop,
    Condition,
    create_task,
    get_running_loop,
    run,
    run_coroutine_threadsafe,
    wait,
    wrap_future,
)
from concurrent.futures import Future as CFuture
from contextlib import contextmanager
from threading import Lock as CLock
from threading import Thread
from typing import Generic, Iterator, TypeVar, cast

_T_co = TypeVar("_T_co")


class Worker(Generic[_T_co]):

    def __init__(self) -> None:
        self._idle = Condition()
        self._interrupt_lock = CLock()
        self._loop: AbstractEventLoop = cast(AbstractEventLoop, None)
        fut = CFuture()

        async def cont() -> None:
            self._loop = get_running_loop()
            fut.set_result(None)
            await self._run()

        self._th = Thread(daemon=True, target=lambda: run(cont()))
        self._th.start()
        fut.result()

    @contextmanager
    def _interrupt(self) -> Iterator[None]:
        with self._interrupt_lock:
            pass
            self._interrupt_fut = CFuture()
            yield

    async def idle(self) -> None:
        async def cont() -> None:
            async with self._idle:
                self._idle.notify_all()

        f = run_coroutine_threadsafe(cont(), self._loop)
        await wrap_future(f)

    @abstractmethod
    async def _run(self) -> None: ...
