from asyncio import new_event_loop, run_coroutine_threadsafe
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Awaitable, TypeVar

loop = new_event_loop()
chan = ThreadPoolExecutor()


T = TypeVar("T")


def schedule(coro: Awaitable[T]) -> T:
    fut: Future[T] = Future()

    def stage() -> None:
        fu = run_coroutine_threadsafe(coro, loop)
        try:
            ret = fu.result()
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(ret)

    chan.submit(stage)
    return fut.result()
