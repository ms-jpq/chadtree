from time import sleep
from typing import Any, Optional, cast

from pynvim import Nvim
from pynvim_pp.client import BasicClient
from pynvim_pp.highlight import highlight
from pynvim_pp.lib import threadsafe_call
from pynvim_pp.rpc import RpcMsg, nil_handler

from .registry import autocmd, rpc
from .settings.load import initial as initial_settings
from .settings.localization import init as init_locale
from .settings.types import Settings
from .state.load import initial as initial_state
from .state.types import State
from .transitions.redraw import redraw
from .transitions.types import Stage


class ChadClient(BasicClient):
    def __init__(self) -> None:
        super().__init__()
        self._state: Optional[State] = None
        self._settings: Optional[Settings] = None

    def on_msg(self, nvim: Nvim, msg: RpcMsg) -> Any:
        name, args = msg
        handler = self._handlers.get(name, nil_handler(name))
        stage = cast(Optional[Stage], handler(nvim, self._state, self._settings, *args))
        if stage:
            self._state = stage.state
            redraw(nvim, state=self._state, focus=stage.focus)

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

        while True:
            sleep(69)
