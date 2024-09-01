from asyncio import (
    AbstractEventLoop,
    Lock,
    Task,
    create_task,
    get_running_loop,
    run,
    run_coroutine_threadsafe,
    wrap_future,
)
from concurrent.futures import Future, InvalidStateError, ThreadPoolExecutor
from contextlib import suppress
from functools import lru_cache, wraps
from threading import Thread
from typing import Any, Awaitable, Callable, Coroutine, Optional, TypeVar, cast

_T = TypeVar("_T")


class AsyncExecutor:
    def __init__(self, threadpool: ThreadPoolExecutor) -> None:
        f: Future = Future()
        self._fut: Future = Future()

        async def cont() -> None:
            loop = get_running_loop()
            loop.set_default_executor(threadpool)
            f.set_result(loop)
            main: Coroutine = await wrap_future(self._fut)
            await main

        self._th = Thread(daemon=True, target=lambda: run(cont()))
        self._th.start()
        self.threadpool = threadpool
        self.loop: AbstractEventLoop = f.result()

    def run(self, main: Awaitable[Any]) -> None:
        self._fut.set_result(main)

    def fsubmit(self, f: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        fut: Future = Future()

        def cont() -> None:
            if fut.set_running_or_notify_cancel():
                try:
                    ret = f(*args, **kwargs)
                except BaseException as e:
                    with suppress(InvalidStateError):
                        fut.set_exception(e)
                else:
                    with suppress(InvalidStateError):
                        fut.set_result(ret)

        self.loop.call_soon_threadsafe(cont)
        return fut

    def submit(self, co: Awaitable[_T]) -> Awaitable[_T]:
        f = run_coroutine_threadsafe(co, loop=self.loop)
        return wrap_future(f)


def Locker() -> Callable[[], Lock]:
    @lru_cache(maxsize=None)
    def lock() -> Lock:
        return Lock()

    return lock


_F = TypeVar("_F", bound=Callable[..., Coroutine])


def Canceller() -> Callable[[_F], _F]:
    task: Optional[Task] = None

    def cont(fn: _F) -> _F:
        @wraps(fn)
        async def wrapped(*__a: Any, **__kw: Any) -> Any:
            nonlocal task
            if t := task:
                t.cancel()
            t = create_task(fn(*__a, **__kw))
            task = t
            return await t

        return cast(_F, wrapped)

    return cont
