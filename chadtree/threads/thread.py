from __future__ import annotations

from abc import abstractmethod
from asyncio import (
    FIRST_COMPLETED,
    AbstractEventLoop,
    Condition,
    create_task,
    get_running_loop,
    run,
    run_coroutine_threadsafe,
    wait,
    wrap_future,
)
from concurrent.futures import Future, InvalidStateError
from contextlib import suppress
from threading import Lock, Thread
from typing import Coroutine, Generic, TypeVar, cast

from std2.asyncio import cancel

_T_co = TypeVar("_T_co")


class Worker(Generic[_T_co]):

    def __init__(self) -> None:
        self._lock = Lock()
        self._idle = Condition()
        self._loop: AbstractEventLoop = cast(AbstractEventLoop, None)
        self._interrupt_fut: Future = Future()
        fut: Future = Future()

        async def cont() -> None:
            self._loop = get_running_loop()
            fut.set_result(None)
            await self._run()

        self._th = Thread(daemon=True, target=lambda: run(cont()))
        self._th.start()
        fut.result()

    def interrupt(self) -> None:
        with suppress(InvalidStateError):
            self._interrupt_fut.set_result(None)
        with self._lock:
            self._interrupt_fut = Future()

    async def _with_interrupt(self, co: Coroutine) -> None:
        with self._lock:
            f = self._interrupt_fut
        fut = wrap_future(f)
        task = create_task(co)
        done, _ = await wait((task, fut), return_when=FIRST_COMPLETED)
        if fut in done:
            await cancel(task)

    async def idle(self) -> None:
        async def cont() -> None:
            async with self._idle:
                self._idle.notify_all()

        f = run_coroutine_threadsafe(cont(), self._loop)
        await wrap_future(f)

    @abstractmethod
    async def _run(self) -> None: ...
