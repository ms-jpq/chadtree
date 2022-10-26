from asyncio import Event, Lock, Task, create_task, gather
from contextlib import suppress
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
from std2.cell import RefCell
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
    await enqueue_event(False, method=vc_refresh.method)

    async for _ in aticker(settings.polling_rate, immediately=False):
        await enqueue_event(False, method=scheduled_update.method)
        await enqueue_event(False, method=vc_refresh.method)
        await enqueue_event(False, method=save_session.method)


def _trans(handler: _CB) -> _CB:
    @wraps(handler)
    async def f(*params: Any) -> None:
        await enqueue_event(True, method=handler.method, params=params)

    return cast(_CB, f)


async def _default(_: MsgType, method: Method, params: Sequence[Any]) -> None:
    await enqueue_event(True, method=method, params=params)


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
            state = RefCell(await initial_state(settings))

            init_locale(settings.lang)

            for f in handlers.values():
                ff = _trans(f)
                client.register(ff)

            staged = RefCell[Optional[Stage]](None)
            event = Event()
            lock = Lock()

            async def step(
                prev: Optional[Task], method: Method, params: Sequence[Any]
            ) -> None:
                if prev:
                    await cancel(prev)

                if handler := cast(Optional[_CB], handlers.get(method)):
                    with suppress_and_log():
                        async with lock:
                            if stage := await handler(state.val, settings, *params):
                                state.val = stage.state
                                staged.val = stage
                                event.set()
                else:
                    assert False, (method, params)

            async def c1() -> None:
                task: Optional[Task] = None
                while True:
                    msg: Tuple[bool, Method, Sequence[Any]] = await queue().get()
                    sync, method, params = msg
                    t = create_task(
                        step(
                            task,
                            method=method,
                            params=params,
                        )
                    )
                    task = t if not sync else task

            async def c2() -> None:
                t1, has_drawn = monotonic(), False

                while True:
                    with suppress_and_log():
                        await event.wait()
                        try:
                            if stage := staged.val:
                                state = stage.state

                                for _ in range(RENDER_RETRIES - 1):
                                    with suppress(NvimError):
                                        await redraw(state, focus=stage.focus)
                                        break
                                else:
                                    try:
                                        await redraw(state, focus=stage.focus)
                                    except NvimError as e:
                                        log.warn("%s", e)

                                if settings.profiling and not has_drawn:
                                    has_drawn = True
                                    await _profile(t1=t1)
                        finally:
                            event.clear()

            await gather(c1(), c2(), _sched(settings))
