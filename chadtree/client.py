from asyncio import run_coroutine_threadsafe
from queue import SimpleQueue
from typing import Any, MutableMapping, Optional, cast

from pynvim import Nvim
from pynvim_pp.client import Client
from pynvim_pp.highlight import highlight
from pynvim_pp.lib import threadsafe_call
from pynvim_pp.logging import log
from pynvim_pp.rpc import RpcCallable, RpcMsg, nil_handler
from std2.sched import ticker
from std2.types import AnyFun

from ._registry import ____
from .registry import autocmd, rpc
from .settings.load import initial as initial_settings
from .settings.localization import init as init_locale
from .settings.types import Settings
from .state.load import initial as initial_state
from .state.types import State
from .transitions.autocmds import save_session, schedule_update
from .transitions.redraw import redraw
from .transitions.types import Stage


class ChadClient(Client):
    def __init__(self) -> None:
        self._q: SimpleQueue = SimpleQueue()
        self._handlers: MutableMapping[str, RpcCallable] = {}
        self._state: Optional[State] = None
        self._settings: Optional[Settings] = None

    def on_msg(self, nvim: Nvim, msg: RpcMsg) -> Any:
        self._q.put(msg)
        return None

    def wait(self, nvim: Nvim) -> int:
        def cont() -> None:
            atomic, specs = rpc.drain(nvim.channel_id)
            self._handlers.update(specs)
            self._settings = initial_settings(nvim, specs)
            hl_ctx = self._settings.view.hl_context
            hl = highlight(*hl_ctx.groups)
            (atomic + autocmd.drain() + hl).commit(nvim)

            self._state = initial_state(nvim, settings=self._settings)
            init_locale(self._settings.lang)

        threadsafe_call(nvim, cont)

        async def sched() -> None:
            period = cast(Settings, self._settings).polling_rate
            async for _ in ticker(period, immediately=False):
                self._q.put((schedule_update.name, ()))
                self._q.put((save_session.name, ()))

        run_coroutine_threadsafe(sched(), loop=nvim.loop)

        while True:
            msg: RpcMsg = self._q.get()
            name, args = msg
            handler = self._handlers.get(name, nil_handler(name))

            def cont() -> None:
                stage = cast(AnyFun[Optional[Stage]], handler)(
                    nvim, self._state, self._settings, *args
                )
                if stage:
                    self._state = stage.state
                    redraw(nvim, state=self._state, focus=stage.focus)

            try:
                threadsafe_call(nvim, cont)
            except Exception as e:
                log.exception("%s", e)
