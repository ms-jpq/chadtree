from asyncio.events import AbstractEventLoop
from contextlib import nullcontext, suppress
from sys import stderr
from typing import Any, MutableMapping, Optional, cast

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim_pp.client import Client
from pynvim_pp.highlight import highlight
from pynvim_pp.lib import threadsafe_call, write
from pynvim_pp.logging import log
from pynvim_pp.rpc import RpcCallable, RpcMsg, nil_handler
from std2.pickle import DecodeError
from std2.sched import ticker
from std2.timeit import timeit
from std2.types import AnyFun

from ._registry import ____
from .consts import WARN_DURATION
from .registry import autocmd, enqueue_event, event_queue, pool, rpc
from .settings.load import initial as initial_settings
from .settings.localization import init as init_locale
from .settings.types import Settings
from .state.load import initial as initial_state
from .state.types import State
from .transitions.autocmds import save_session
from .transitions.redraw import redraw
from .transitions.schedule_update import schedule_update
from .transitions.types import Stage
from .transitions.version_ctl import vc_refresh


class ChadClient(Client):
    def __init__(self) -> None:
        self._handlers: MutableMapping[str, RpcCallable] = {}
        self._state: Optional[State] = None
        self._settings: Optional[Settings] = None

    def on_msg(self, nvim: Nvim, msg: RpcMsg) -> Any:
        event_queue.put(msg)
        return None

    def wait(self, nvim: Nvim) -> int:
        def cont() -> None:
            if isinstance(nvim.loop, AbstractEventLoop):
                nvim.loop.set_default_executor(pool)

            atomic, specs = rpc.drain(nvim.channel_id)
            self._handlers.update(specs)
            self._settings = initial_settings(nvim, specs)
            hl = highlight(*self._settings.view.hl_context.groups)
            (atomic + autocmd.drain() + hl).commit(nvim)

            self._state = initial_state(nvim, settings=self._settings)
            init_locale(self._settings.lang)

        try:
            threadsafe_call(nvim, cont)
        except DecodeError as e:
            print(e, file=stderr)
            return 1
        except Exception as e:
            log.exception("%s", e)
            return 1

        def sched() -> None:
            period = cast(Settings, self._settings).polling_rate
            enqueue_event(vc_refresh)
            for _ in ticker(period, immediately=False):
                enqueue_event(schedule_update)
                enqueue_event(vc_refresh)
                enqueue_event(save_session)

        pool.submit(sched)

        while True:
            msg: RpcMsg = event_queue.get()
            name, args = msg
            handler = self._handlers.get(name, nil_handler(name))

            def cont() -> None:
                stage = cast(AnyFun[Optional[Stage]], handler)(
                    nvim, self._state, self._settings, *args
                )
                if stage:
                    self._state = stage.state
                    mgr = suppress(NvimError) if stage.silent else nullcontext()
                    with mgr, timeit() as t:
                        redraw(nvim, state=self._state, focus=stage.focus)
                    # duration = t()
                    # write(nvim, round(duration, 3))

            try:
                threadsafe_call(nvim, cont)
            except Exception as e:
                log.exception("%s", e)
