from asyncio.locks import Lock
from asyncio.tasks import sleep
from math import inf
from typing import Any, Awaitable, MutableMapping, Optional

from pynvim import Nvim
from pynvim_pp.client import Client
from pynvim_pp.highlight import highlight
from pynvim_pp.lib import async_call, go, write
from pynvim_pp.rpc import RpcCallable, RpcMsg, nil_handler

from .consts import DEFAULT_LANG, LANG_ROOT
from .localization import init as init_locale
from .settings import initial as initial_settings
from .state import initial as initial_state
from .transitions import redraw
from .types import Settings, Stage, State


class ChadClient(Client):
    def __init__(self) -> None:
        self._lock = Lock()
        self._handlers: MutableMapping[str, RpcCallable] = {}
        self._state: Optional[State] = None
        self._settings: Optional[Settings] = None

    def _submit(self, nvim: Nvim, aw: Awaitable[Optional[Stage]]) -> None:
        async def cont() -> None:
            async with self._lock:
                stage = await aw
                if stage:
                    self._state = stage.state
                    await redraw(nvim, state=self._state, focus=stage.focus)

        go(cont())

    def on_msg(self, nvim: Nvim, msg: RpcMsg) -> Any:
        name, args = msg
        handler = self._handlers.get(name, nil_handler(name))
        ret = handler(nvim, state=self._state, settings=self._settings, *args)
        if isinstance(ret, Awaitable):
            self._submit(nvim, aw=ret)
            return None
        else:
            return ret

    async def wait(self, nvim: Nvim) -> int:
        def cont() -> None:
            settings = initial_settings(nvim)
            init_locale(LANG_ROOT, code=settings.lang, fallback=DEFAULT_LANG)

        await async_call(nvim, cont)
        return await sleep(inf, 1)
