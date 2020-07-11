from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from json import load
from typing import Any, Callable, TypeVar, cast

T = TypeVar("T")


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
