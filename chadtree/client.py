from typing import Any, Optional, cast

from pynvim import Nvim
from pynvim_pp.client import BasicClient
from pynvim_pp.highlight import highlight
from pynvim_pp.lib import async_call, write
from pynvim_pp.rpc import RpcMsg, nil_handler

from .localization import init as init_locale
from .registry import autocmd, rpc
from .settings import initial as initial_settings
from .state import initial as initial_state
from .transitions import redraw
from .types import Settings, Stage, State


class ChadClient(BasicClient):
    def __init__(self) -> None:
        super().__init__()
        self._state: Optional[State] = None
        self._settings: Optional[Settings] = None

    def on_msg(self, nvim: Nvim, msg: RpcMsg) -> Any:
        name, args = msg
        handler = self._handlers.get(name, nil_handler(name))
        if handler.is_async:

            async def cont() -> None:
                stage: Optional[Stage] = await handler(
                    nvim, state=self._state, settings=self._settings, *args
                )
                if stage:
                    self._state = stage.state
                    await redraw(nvim, state=self._state, focus=stage.focus)

            self._q.put((name, args, cont()))
        else:
            assert False

    async def wait(self, nvim: Nvim) -> int:
        def cont() -> None:
            atomic, specs = rpc.drain(nvim.channel_id)
            self._handlers.update(specs)
            self._settings = initial_settings(nvim, specs)
            hl_ctx = self._settings.view.hl_context
            hl = highlight(*hl_ctx.groups)
            (atomic + autocmd.drain() + hl).commit(nvim)

        await async_call(nvim, cont)
        self._state = await initial_state(nvim, settings=cast(Settings, self._settings))
        init_locale(cast(Settings, self._settings).lang)
        return await super().wait(nvim)
