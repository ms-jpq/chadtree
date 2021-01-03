from functools import partial
from itertools import count
from json import dump, load
from operator import pow
from pathlib import Path
from typing import Any,  Optional, TypeVar, Union, cast

from .consts import folder_mode

T = TypeVar("T")


class Void:
    def __bool__(self) -> bool:
        return False

    def __eq__(self, o: Any) -> bool:
        return type(o) is Void

    def __str__(self) -> str:
        return type(self).__name__


def or_else(thing: Union[T, Void], default: T) -> T:
    return default if thing == Void() else cast(T, thing)


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


def load_json(path: Path) -> Optional[Any]:
    if path.exists():
        with path.open(encoding="utf8") as fd:
            return load(fd)
    else:
        return None


def dump_json(path: Path, json: Any) -> None:
    path.parent.mkdir(mode=folder_mode, parents=True, exist_ok=True)
    with path.open("w") as fd:
        return dump(json, fd, ensure_ascii=False, indent=2)
