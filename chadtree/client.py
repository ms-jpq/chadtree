from asyncio.events import AbstractEventLoop
from concurrent.futures import Executor
from multiprocessing import cpu_count
from pathlib import Path
from platform import uname
from string import Template
from sys import executable
from textwrap import dedent
from time import monotonic
from typing import Any, MutableMapping, Optional, cast

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim_pp.client import Client
from pynvim_pp.highlight import highlight
from pynvim_pp.lib import threadsafe_call, write
from pynvim_pp.logging import log, with_suppress
from pynvim_pp.rpc import RpcCallable, RpcMsg, nil_handler
from std2.pickle.types import DecodeError
from std2.sched import ticker
from std2.types import AnyFun

from ._registry import ____
from .consts import RENDER_RETRIES
from .registry import autocmd, enqueue_event, event_queue, rpc
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


def _profile(nvim: Nvim, t1: float) -> None:
    t2 = monotonic()
    info = uname()
    msg = f"""
    First msg  {int((t2 - t1) * 1000)}ms
    Arch       {info.machine}
    Processor  {info.processor}
    Cores      {cpu_count()}
    System     {info.system}
    Version    {info.version}
    Python     {Path(executable).resolve(strict=True)}
    """
    write(nvim, dedent(msg))


class ChadClient(Client):
    def __init__(self, pool: Executor) -> None:
        self._pool = pool
        self._handlers: MutableMapping[str, RpcCallable] = {}
        self._state: Optional[State] = None
        self._settings: Optional[Settings] = None

    def on_msg(self, nvim: Nvim, msg: RpcMsg) -> Any:
        event_queue.put(msg)
        return None

    def wait(self, nvim: Nvim) -> int:
        def cont() -> bool:
            assert isinstance(nvim.loop, AbstractEventLoop)
            nvim.loop.set_default_executor(self._pool)

            atomic, specs = rpc.drain(nvim.channel_id)
            self._handlers.update(specs)
            try:
                self._settings = initial_settings(nvim, specs)
            except DecodeError as e:
                tpl = """
                Some options may have changed.
                See help doc on Github under [docs/CONFIGURATION.md]


                ${e}
                """
                ms = Template(dedent(tpl)).substitute(e=e)
                write(nvim, ms, error=True)
                return False
            else:
                hl = highlight(*self._settings.view.hl_context.groups)
                (atomic + autocmd.drain() + hl).commit(nvim)

                self._state = initial_state(
                    nvim, pool=self._pool, settings=self._settings
                )
                init_locale(self._settings.lang)
                return True

        try:
            go = threadsafe_call(nvim, cont)
        except Exception as e:
            log.exception("%s", e)
            return 1
        else:
            if not go:
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

        self._pool.submit(sched)

        while True:
            msg: RpcMsg = event_queue.get()
            name, args = msg
            handler = cast(
                AnyFun[Optional[Stage]], self._handlers.get(name, nil_handler(name))
            )

            def cdraw() -> None:
                nonlocal has_drawn
                if stage := handler(nvim, self._state, settings, *args):
                    self._state = stage.state

                    for _ in range(RENDER_RETRIES - 1):
                        try:
                            redraw(nvim, state=self._state, focus=stage.focus)
                        except NvimError:
                            pass
                        else:
                            break
                    else:
                        try:
                            redraw(nvim, state=self._state, focus=stage.focus)
                        except NvimError as e:
                            log.warn("%s", e)

                    if settings.profiling and not has_drawn:
                        has_drawn = True
                        _profile(nvim, t1=t1)

            with with_suppress():
                threadsafe_call(nvim, cdraw)
