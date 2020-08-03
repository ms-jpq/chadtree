from asyncio import create_subprocess_exec, get_running_loop
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from functools import partial
from itertools import count
from json import dump, load
from operator import pow
from os import makedirs
from os.path import dirname, exists
from subprocess import CompletedProcess, run
from sys import version_info
from typing import Any, Callable, Optional, TypeVar, cast

from .consts import folder_mode

T = TypeVar("T")


def merge(ds1: Any, ds2: Any, replace: bool = False) -> Any:
    if type(ds1) is dict and type(ds2) is dict:
        append = {k: merge(ds1.get(k), v, replace) for k, v in ds2.items()}
        return {**ds1, **append}
    if type(ds1) is list and type(ds2) is list:
        if replace:
            return ds2
        else:
            return [*ds1, *ds2]
    else:
        return ds2


def merge_all(ds1: Any, *dss: Any, replace: bool = False) -> Any:
    res = ds1
    for ds2 in dss:
        res = merge(res, ds2, replace=replace)
    return res


def or_else(thing: Optional[T], default: T) -> T:
    return default if thing is None else thing


def constantly(val: T) -> Callable[[Any], T]:
    def ret(*args: Any, **kwargs: Any) -> T:
        return val

    return ret


def human_readable_size(size: int, truncate: int = 3) -> str:
    units = ("", "K", "M", "G", "T", "P", "E", "Z", "Y")
    step = partial(pow, 10)
    steps = zip(map(step, count(step=3)), units)
    for factor, unit in steps:
        divided = size / factor
        if abs(divided) < 1000:
            fmt = format(divided, f".{truncate}f").rstrip("0").rstrip(".")
            return f"{fmt}{unit}"

    raise ValueError(f"unit over flow: {size}")


@dataclass(frozen=True)
class ProcReturn:
    code: int
    out: str
    err: str


if (version_info.major, version_info.minor) == (3, 7):

    async def call(prog: str, *args: str) -> ProcReturn:
        loop = get_running_loop()

        def cont() -> CompletedProcess:
            return run((prog, *args), capture_output=True)

        ret = await loop.run_in_executor(None, cont)
        out, err = ret.stdout.decode(), ret.stderr.decode()
        code = ret.returncode
        return ProcReturn(code=code, out=out, err=err)


else:

    async def call(prog: str, *args: str) -> ProcReturn:
        proc = await create_subprocess_exec(prog, *args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = await proc.communicate()
        code = cast(int, proc.returncode)
        return ProcReturn(code=code, out=stdout.decode(), err=stderr.decode())


def load_json(path: str) -> Optional[Any]:
    if exists(path):
        with open(path, encoding="utf8") as fd:
            return load(fd)
    else:
        return None


def dump_json(path: str, json: Any) -> None:
    parent = dirname(path)
    makedirs(parent, mode=folder_mode, exist_ok=True)
    with open(path, "w") as fd:
        return dump(json, fd, ensure_ascii=False, indent=2)
