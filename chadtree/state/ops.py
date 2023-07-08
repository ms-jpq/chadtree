from hashlib import sha1
from json import dumps, loads
from os.path import normcase
from pathlib import Path, PurePath
from tempfile import NamedTemporaryFile
from typing import Any, MutableMapping, Optional

from pynvim_pp.lib import decode, encode
from std2.asyncio import to_thread
from std2.pickle.decoder import new_decoder
from std2.pickle.encoder import new_encoder

from .types import Session, State, StoredSession

_DECODER = new_decoder[StoredSession](StoredSession)
_ENCODER = new_encoder[StoredSession](StoredSession)


def _session_path(cwd: PurePath, storage: Path) -> Path:
    hashed = sha1(normcase(cwd).encode()).hexdigest()
    part = storage / hashed
    return part.with_suffix(".json")


async def _load_json(path: Path) -> Optional[Any]:
    def cont() -> Optional[Any]:
        try:
            json = decode(path.read_bytes())
        except FileNotFoundError:
            return None
        else:
            return loads(json)

    return await to_thread(cont)


async def load_session(session: Session) -> StoredSession:
    load_path = _session_path(session.workdir, storage=session.storage)
    try:
        json = await _load_json(load_path)
        if isinstance(json, MutableMapping):
            json.pop("bookmarks", None)
        sessions = _DECODER(json)
    except Exception:
        return StoredSession(index=frozenset(), show_hidden=None, enable_vc=None)
    else:
        return sessions


async def dump_session(state: State) -> None:
    stored = StoredSession(
        index=state.index,
        show_hidden=state.show_hidden,
        enable_vc=state.enable_vc,
    )

    json = _ENCODER(stored)
    path = _session_path(state.session.workdir, storage=state.session.storage)
    parent = path.parent
    dumped = encode(dumps(json, ensure_ascii=False, check_circular=False, indent=2))

    def cont() -> None:
        parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=parent, delete=False) as f:
            f.write(dumped)

        Path(f.name).replace(path)

    await to_thread(cont)
