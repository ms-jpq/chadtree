from dataclasses import dataclass
from hashlib import sha1
from json import dump
from pathlib import Path

from std2.pickle import decode, encode

from ..consts import SESSION_DIR, FOLDER_MODE
from ..da import load_json
from ..fs.types import Index
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
    json = encode(_Session(index=state.index, show_hidden=state.show_hidden))

    path = _session_path(state.root.path)
    path.parent.mkdir(mode=FOLDER_MODE, parents=True, exist_ok=True)
    with path.open("w") as fd:
        dump(json, fd, ensure_ascii=False, check_circular=False, indent=2)
