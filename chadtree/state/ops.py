from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Optional

from std2.pickle import decode, encode

from ..consts import SESSION_DIR
from ..da import dump_json, load_json
from ..fs.types import Node, Index
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


def index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.derived.lookup)):
        return state.derived.lookup[row]
    else:
        return None
