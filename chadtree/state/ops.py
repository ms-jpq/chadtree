from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Iterator, Optional, Sequence

from pynvim.api import Buffer, Nvim, Window
from std2.pickle import decode, encode

from ..consts import SESSION_DIR
from ..da import dump_json, load_json
from ..fs.types import Index, Node
from ..nvim.wm import is_fm_buffer
from .types import State


@dataclass(frozen=True)
class _Session:
    index: Index
    show_hidden: bool


def _session_path(cwd: str) -> Path:
    hashed = sha1(cwd.encode()).hexdigest()
    part = SESSION_DIR / hashed
    return part.with_suffix(".json")


def load_session(cwd: str) -> _Session:
    load_path = _session_path(cwd)
    try:
        return decode(_Session, load_json(load_path))
    except Exception:
        return _Session(index=frozenset((cwd,)), show_hidden=False)


def dump_session(state: State) -> None:
    load_path = _session_path(state.root.path)
    json = _Session(index=state.index, show_hidden=state.show_hidden)
    dump_json(load_path, encode(json))


def _row_index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.derived.lookup)):
        return state.derived.lookup[row]
    else:
        return None


def index(nvim: Nvim, state: State) -> Optional[Node]:
    window: Window = nvim.api.get_current_win()
    buffer: Buffer = nvim.api.win_get_buf(window)
    if is_fm_buffer(nvim, buffer=buffer):
        row, _ = nvim.api.win_get_cursor(window)
        row = row - 1
        return _row_index(state, row)
    else:
        return None


def indices(nvim: Nvim, state: State, is_visual: bool) -> Sequence[Node]:
    def step() -> Iterator[Node]:
        if is_visual:
            buffer: Buffer = nvim.api.get_current_buf()
            r1, _ = nvim.api.buf_get_mark(buffer, "<")
            r2, _ = nvim.api.buf_get_mark(buffer, ">")
            for row in range(r1 - 1, r2):
                node = _row_index(state, row)
                if node:
                    yield node
        else:
            window: Window = nvim.api.get_current_win()
            row, _ = nvim.api.win_get_cursor(window)
            row = row - 1
            node = _row_index(state, row)
            if node:
                yield node

    return tuple(step())
