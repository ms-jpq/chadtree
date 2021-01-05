from functools import partial
from itertools import count
from json import dump, load
from operator import pow
from pathlib import Path
from typing import Any, Optional

from .consts import folder_mode


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
