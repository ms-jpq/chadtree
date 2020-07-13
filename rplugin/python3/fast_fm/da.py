from asyncio import TimerHandle, create_subprocess_exec, get_running_loop
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from functools import partial
from json import load
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Optional,
    Protocol,
    TypeVar,
    cast,
)

T = TypeVar("T")


def or_else(thing: Optional[T], default: T) -> T:
    return default if thing is None else thing


async def anext(aiter: AsyncIterator[T], default: Optional[T] = None) -> Optional[T]:
    try:
        return await aiter.__anext__()
    except StopAsyncIteration:
        return default


def constantly(val: T) -> Callable[[Any], T]:
    def ret(*args: Any, **kwargs: Any) -> T:
        return val

    return ret


class AnyCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass


class AnyCallableAsync(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[Any]:
        pass


async def resolve(val: T) -> T:
    return val


def async_throttle(delay_seconds: float):
    def decor(fn: AnyCallableAsync) -> AnyCallableAsync:
        throttling = False
        handle: Optional[TimerHandle] = None

        def unthrottle() -> None:
            nonlocal throttling
            throttling = False

        def throttled(*args: Any, **kwargs: Any) -> Any:
            nonlocal throttling
            if throttling:
                return resolve(None)
            else:
                throttling = True
                loop = get_running_loop()
                loop.call_later(delay_seconds, unthrottle)
                return fn(*args, **kwargs)

        def run(*args: Any, **kwargs: Any) -> Any:
            nonlocal handle
            if handle:
                handle.cancel()
            if throttling:
                f = partial(throttled, *args, **kwargs)
                loop = get_running_loop()
                handle = loop.call_later(delay_seconds, f)
                return resolve(None)
            else:
                return throttled(*args, **kwargs)

        return run

    return decor


@dataclass(frozen=True)
class ProcReturn:
    code: int
    out: str
    err: str


async def call(prog: str, *args: str) -> ProcReturn:
    proc = await create_subprocess_exec(prog, *args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    code = cast(int, proc.returncode)
    return ProcReturn(code=code, out=stdout.decode(), err=stderr.decode())


def load_json(path: str) -> Any:
    with open(path) as fd:
        return load(fd)
