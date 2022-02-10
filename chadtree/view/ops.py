from os import sep
from os.path import relpath
from pathlib import Path, PurePath
from string import whitespace

from ..state.types import State

_WS = {*whitespace} - {"\t"}


def encode_for_display(text: str) -> str:
    encoded = "".join(
        char.encode("unicode_escape").decode("utf-8") if char in _WS else char
        for char in text
    )
    return encoded


def display_path(path: PurePath, state: State) -> str:
    raw = relpath(path, start=state.root.path)
    name = encode_for_display(raw)
    if Path(path).is_dir():
        return f"{name}{sep}"
    else:
        return name
