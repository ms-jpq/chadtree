from dataclasses import dataclass
from hashlib import sha1
from json import dump
from pathlib import Path

from std2.pickle import decode, encode

from ..consts import FOLDER_MODE, SESSION_DIR
from ..da import load_json
from .types import Session, State


def _session_path(cwd: str) -> Path:
    hashed = sha1(cwd.encode()).hexdigest()
    part = SESSION_DIR / hashed
    return part.with_suffix(".json")


def load_session(cwd: str) -> Session:
    load_path = _session_path(cwd)
    try:
        return decode(Session, load_json(load_path))
    except Exception:
        return Session(index={cwd}, show_hidden=False, enable_vc=True)


def dump_session(state: State) -> None:
    session = Session(
        index=state.index, show_hidden=state.show_hidden, enable_vc=state.enable_vc
    )
    json = encode(session)

    path = _session_path(state.root.path)
    path.parent.mkdir(mode=FOLDER_MODE, parents=True, exist_ok=True)
    with path.open("w") as fd:
        dump(json, fd, ensure_ascii=False, check_circular=False, indent=2)
