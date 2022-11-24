from asyncio import Lock
from functools import lru_cache
from hashlib import sha1
from json import dumps, loads
from pathlib import Path, PurePath
from typing import Any, Optional

from pynvim_pp.lib import decode
from std2.asyncio import to_thread
from std2.pickle.decoder import new_decoder
from std2.pickle.encoder import new_encoder

from .types import Session, State


@lru_cache(maxsize=None)
def _lock() -> Lock:
    return Lock()


def _session_path(cwd: PurePath, session_store: Path) -> Path:
    hashed = sha1(str(cwd).encode()).hexdigest()
    part = session_store / hashed
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


_DECODER = new_decoder[Session](Session)
_ENCODER = new_encoder[Session](Session)


async def load_session(cwd: PurePath, session_store: Path) -> Session:
    load_path = _session_path(cwd, session_store=session_store)
    try:
        session = _DECODER(await _load_json(load_path))
        return session
    except Exception:
        return Session(index=None, show_hidden=None, enable_vc=None)


async def dump_session(state: State, session_store: Path) -> None:
    session = Session(
        index=state.index, show_hidden=state.show_hidden, enable_vc=state.enable_vc
    )

    json = _ENCODER(session)
    path = _session_path(state.root.path, session_store=session_store)

    def cont() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        dumped = dumps(json, ensure_ascii=False, check_circular=False, indent=2)
        path.write_text(dumped, "UTF-8")

    async with _lock():
        await to_thread(cont)
