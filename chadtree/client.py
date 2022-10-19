from asyncio import create_task, gather
from functools import wraps
from multiprocessing import cpu_count
from pathlib import Path
from platform import uname
from string import Template
from sys import executable, exit
from textwrap import dedent
from time import monotonic
from typing import Any, Optional, Sequence, Tuple, cast

from pynvim_pp.highlight import highlight
from pynvim_pp.logging import log, suppress_and_log
from pynvim_pp.nvim import Nvim, conn
from pynvim_pp.rpc import MsgType, ServerAddr
from pynvim_pp.types import Method, NoneType, NvimError, RPCallable
from std2.asyncio import cancel
from std2.pickle.types import DecodeError
from std2.sched import aticker

from ._registry import ____
from .consts import RENDER_RETRIES
from .registry import autocmd, enqueue_event, queue, rpc
from .settings.load import initial as initial_settings
from .settings.localization import init as init_locale
from .settings.types import Settings
from .state.load import initial as initial_state
from .transitions.autocmds import save_session
from .transitions.redraw import redraw
from .transitions.schedule_update import scheduled_update
from .transitions.types import Stage
from .transitions.version_ctl import vc_refresh

assert ____ or True

_CB = RPCallable[Optional[Stage]]


async def _profile(t1: float) -> None:
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
    await Nvim.write(dedent(msg))


async def _sched(settings: Settings) -> None:
    await enqueue_event(vc_refresh.method)

    async for _ in aticker(settings.polling_rate, immediately=False):
        await enqueue_event(scheduled_update.method)
        await enqueue_event(vc_refresh.method)
        await enqueue_event(save_session.method)


def _trans(handler: _CB) -> _CB:
    @wraps(handler)
    async def f(*params: Any) -> None:
        await enqueue_event(handler.method, *params)

    return cast(_CB, f)


async def _default(_: MsgType, method: Method, params: Sequence[Any]) -> None:
    await enqueue_event(method, *params)


async def init(socket: ServerAddr) -> None:
    async with conn(socket, default=_default) as client:
        atomic, handlers = rpc.drain()
        try:
            settings = await initial_settings(handlers.values())
        except DecodeError as e:
            tpl = """
            Some options may have changed.
            See help doc on Github under [docs/CONFIGURATION.md]


            ${e}
            """
            ms = Template(dedent(tpl)).substitute(e=e)
            await Nvim.write(ms, error=True)
            exit(1)
        else:
            hl = highlight(*settings.view.hl_context.groups)
            await (atomic + autocmd.drain() + hl).commit(NoneType)
            state = await initial_state(settings)

            init_locale(settings.lang)

            for f in handlers.values():
                ff = _trans(f)
                client.register(ff)

            async def cont() -> None:
                nonlocal state
                t1, has_drawn = monotonic(), False

                task = None
                while True:
                    with suppress_and_log():
                        msg: Tuple[Method, Sequence[Any]] = await queue().get()
                        method, params = msg
                        if handler := cast(Optional[_CB], handlers.get(method)):
                            if task:
                                await cancel(task)
                            task = create_task(handler(state, settings, *params))
                            if stage := await task:
                                state = stage.state

                                for _ in range(RENDER_RETRIES - 1):
                                    try:
                                        await redraw(state, focus=stage.focus)
                                    except NvimError:
                                        pass
                                    else:
                                        break
                                else:
                                    try:
                                        await redraw(state, focus=stage.focus)
                                    except NvimError as e:
                                        log.warn("%s", e)

                                if settings.profiling and not has_drawn:
                                    has_drawn = True
                                    await _profile(t1=t1)

                        else:
                            assert False, msg

            await gather(cont(), _sched(settings))
