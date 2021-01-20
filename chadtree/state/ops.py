from hashlib import sha1
from json import dump, load
from pathlib import Path
from typing import Any, Optional

from std2.pickle import decode, encode

from ..consts import FOLDER_MODE, SESSION_DIR
from .types import Session, State


def _session_path(cwd: str) -> Path:
    hashed = sha1(cwd.encode()).hexdigest()
    part = SESSION_DIR / hashed
    return part.with_suffix(".json")


def _load_json(path: Path) -> Optional[Any]:
    if path.exists():
        with path.open(encoding="utf8") as fd:
            return load(fd)
    else:
        return None


def load_session(cwd: str) -> Session:
    load_path = _session_path(cwd)
    try:
        return decode(Session, _load_json(load_path))
    except Exception:
        return Session(index=None, show_hidden=None, enable_vc=None)


def dump_session(state: State) -> None:
    session = Session(
        index=state.index, show_hidden=state.show_hidden, enable_vc=state.enable_vc
    )
    json = encode(session)

    path = _session_path(state.root.path)
    path.parent.mkdir(mode=FOLDER_MODE, parents=True, exist_ok=True)
    with path.open("w") as fd:
        dump(json, fd, ensure_ascii=False, check_circular=False, indent=2)
