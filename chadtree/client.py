from asyncio.events import AbstractEventLoop
from contextlib import nullcontext, suppress
from os import linesep
from sys import stderr
from time import monotonic
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
from std2.types import AnyFun

from ._registry import ____
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
            msg1 = "Some options may hanve changed."
            msg2 = "See help doc on Github under [docs/CONFIGURATION.md]"
            print(e, msg1, msg2, sep=linesep, file=stderr)
            return 1
        except Exception as e:
            log.exception("%s", e)
            return 1
        else:
            settings = cast(Settings, self._settings)
            t1, has_drawn = monotonic(), False

        def sched() -> None:
            enqueue_event(vc_refresh)
            for _ in ticker(settings.polling_rate, immediately=False):
                enqueue_event(schedule_update)
                enqueue_event(vc_refresh)
                enqueue_event(save_session)

        pool.submit(sched)

        while True:
            msg: RpcMsg = event_queue.get()
            name, args = msg
            handler = self._handlers.get(name, nil_handler(name))

            def cont() -> None:
                nonlocal has_drawn
                stage = cast(AnyFun[Optional[Stage]], handler)(
                    nvim, self._state, settings, *args
                )
                if stage:
                    self._state = stage.state
                    mgr = suppress(NvimError) if stage.silent else nullcontext()
                    with mgr:
                        redraw(nvim, state=self._state, focus=stage.focus)
                        if settings.profiling and not has_drawn:
                            has_drawn = True
                            t2 = monotonic()
                            write(nvim, f"{int((t2 - t1) * 1000)}ms")

            try:
                threadsafe_call(nvim, cont)
            except Exception as e:
                log.exception("%s", e)
