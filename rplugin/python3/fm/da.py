from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from json import load
from os.path import dirname, sep
from typing import Any, AsyncIterator, Callable, Iterator, Optional, Set, TypeVar, cast

T = TypeVar("T")


def or_else(thing: Optional[T], default: T) -> T:
    return default if thing is None else thing


async def anext(aiter: AsyncIterator[T], default: Optional[T]) -> Optional[T]:
    try:
        return await aiter.__anext__()
    except StopAsyncIteration:
        return default


def constantly(val: T) -> Callable[[Any], T]:
    def ret(*args: Any, **kwargs: Any) -> T:
        return val

    return ret


def toggled(s: Set[T], i: T) -> Set[T]:
    if i in s:
        return s - {i}
    else:
        return s | {i}


def ancestors(path: str) -> Iterator[str]:
    if not path or path == sep:
        return
    else:
        parent = dirname(path)
        yield from ancestors(parent)
        yield parent


def unify(paths: Set[str]) -> Iterator[str]:
    for path in paths:
        if not any(a in paths for a in ancestors(path)):
            yield path


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
