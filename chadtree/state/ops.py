from hashlib import sha1
from json import dumps, loads
from pathlib import Path, PurePath
from typing import Any, Optional

from std2.pickle import decode, encode
from std2.pickle.coders import BUILTIN_ENCODERS

from ..consts import FOLDER_MODE, SESSION_DIR, SESSION_DIR_XDG
from .types import Session, State


def _session_path(cwd: PurePath, use_xdg: bool) -> Path:
    hashed = sha1(str(cwd).encode()).hexdigest()
    part = (SESSION_DIR_XDG if use_xdg else SESSION_DIR) / hashed
    return part.with_suffix(".json")


def _load_json(path: Path) -> Optional[Any]:
    if path.exists():
        json = path.read_text("UTF-8")
        return loads(json)
    else:
        return None


def load_session(cwd: PurePath, use_xdg: bool) -> Session:
    load_path = _session_path(cwd, use_xdg=use_xdg)
    try:
        return decode(Session, _load_json(load_path))
    except Exception:
        return Session(index=None, show_hidden=None, enable_vc=None)


def dump_session(state: State, use_xdg: bool) -> None:
    session = Session(
        index=state.index, show_hidden=state.show_hidden, enable_vc=state.enable_vc
    )
    json = encode(session, encoders=BUILTIN_ENCODERS)

    path = _session_path(state.root.path, use_xdg=use_xdg)
    path.parent.mkdir(mode=FOLDER_MODE, parents=True, exist_ok=True)
    json = dumps(json, ensure_ascii=False, check_circular=False, indent=2)
    path.write_text(json, "UTF-8")

