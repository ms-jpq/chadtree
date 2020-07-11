from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from json import load
from typing import Any, AsyncIterator, Callable, Optional, TypeVar, cast

T = TypeVar("T")


def or_else(thing: Optional[T], default: T) -> T:
    return default if thing is None else thing


async def anext(aiter: AsyncIterator[T], default: Optional[T]) -> Optional[T]:
    try:
        return await aiter.__anext__()
    except StopAsyncIteration:
        return default


def constantly(val: T) -> Callable[[Any], T]:
    def ret(*args: Any) -> T:
        return val

    return ret


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
