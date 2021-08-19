from hashlib import sha1
from json import dumps, loads
from pathlib import Path, PurePath
from typing import Any, Optional

from std2.pickle import new_decoder, new_encoder

from ..consts import FOLDER_MODE
from .types import Session, State


def _session_path(cwd: PurePath, session_store: Path) -> Path:
    hashed = sha1(str(cwd).encode()).hexdigest()
    part = session_store / hashed
    return part.with_suffix(".json")


def _load_json(path: Path) -> Optional[Any]:
    if path.exists():
        json = path.read_text("UTF-8")
        return loads(json)
    else:
        return None


_DECODER = new_decoder(Session)
_ENCODER = new_encoder(Session)


def load_session(cwd: PurePath, session_store: Path) -> Session:
    load_path = _session_path(cwd, session_store=session_store)
    try:
        session: Session = _DECODER(_load_json(load_path))
        return session
    except Exception:
        return Session(index=None, show_hidden=None, enable_vc=None)


def dump_session(state: State, session_store: Path) -> None:
    session = Session(
        index=state.index, show_hidden=state.show_hidden, enable_vc=state.enable_vc
    )
    json = _ENCODER(session)

    path = _session_path(state.root.path, session_store=session_store)
    path.parent.mkdir(mode=FOLDER_MODE, parents=True, exist_ok=True)
    json = dumps(json, ensure_ascii=False, check_circular=False, indent=2)
    path.write_text(json, "UTF-8")
