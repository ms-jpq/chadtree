from asyncio import (
    FIRST_COMPLETED,
    AbstractEventLoop,
    Event,
    Lock,
    Task,
    create_task,
    gather,
    get_running_loop,
    wait,
    wrap_future,
)
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import AbstractAsyncContextManager
from dataclasses import replace
from functools import wraps
from logging import DEBUG as DEBUG_LVL
from logging import INFO
from multiprocessing import cpu_count
from pathlib import Path, PurePath
from platform import uname
from string import Template
from sys import executable, exit
from textwrap import dedent
from time import monotonic
from typing import Any, Optional, Sequence, cast

from pynvim_pp.highlight import highlight
from pynvim_pp.logging import log, suppress_and_log
from pynvim_pp.nvim import Nvim, conn
from pynvim_pp.rpc_types import (
    Method,
    MsgType,
    NvimError,
    RPCallable,
    RPClient,
    ServerAddr,
)
from pynvim_pp.types import NoneType
from std2.asyncio import Cancellation, cancel
from std2.cell import RefCell
from std2.contextlib import nullacontext
from std2.pickle.types import DecodeError
from std2.platform import OS, os
from std2.sched import aticker
from std2.sys import autodie

from ._registry import ____
from .consts import DEBUG, RENDER_RETRIES
from .registry import autocmd, dequeue_event, enqueue_event, rpc
from .settings.load import initial as initial_settings
from .settings.localization import init as init_locale
from .state.load import initial as initial_state
from .state.types import State
from .timeit import timeit
from .transitions.autocmds import setup
from .transitions.redraw import redraw
from .transitions.schedule_update import scheduled_update
from .transitions.types import Stage

assert ____ or True

_CB = RPCallable[Optional[Stage]]

_die = Cancellation()


def _autodie(ppid: int) -> AbstractAsyncContextManager:
    if os is OS.windows:
        return nullacontext(None)
    else:
        return autodie(ppid)


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


async def _sched(ref: RefCell[State]) -> None:
    await enqueue_event(False, method=scheduled_update.method, params=(True,))

    async for _ in aticker(ref.val.settings.polling_rate, immediately=False):
        if ref.val.vim_focus:
            await enqueue_event(False, method=scheduled_update.method)


def _trans(handler: _CB) -> _CB:
    @wraps(handler)
    async def f(*params: Any) -> None:
        await enqueue_event(True, method=handler.method, params=params)

    return cast(_CB, f)


async def _default(_: MsgType, method: Method, params: Sequence[Any]) -> None:
    await enqueue_event(True, method=method, params=params)


async def _go(loop: AbstractEventLoop, client: RPClient) -> None:
    th = ThreadPoolExecutor()
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
        state_ref = RefCell(await initial_state(settings, th=th))

        init_locale(settings.lang)
        with suppress_and_log():
            await setup(settings)

        for f in handlers.values():
            ff = _trans(f)
            client.register(ff)

        focus_ref = RefCell[Optional[PurePath]](None)
        event = Event()
        lock = Lock()

        async def step(method: Method, params: Sequence[Any]) -> None:
            if handler := cast(Optional[_CB], handlers.get(method)):
                with suppress_and_log():
                    async with lock:
                        if stage := await handler(state_ref.val, *params):
                            state_ref.val = stage.state
                            focus_ref.val = stage.focus
                            event.set()
            else:
                assert False, (method, params)

        async def c1() -> None:
            transcient: Optional[Task] = None
            get: Optional[Task] = None
            try:
                while True:
                    with suppress_and_log():
                        get = create_task(dequeue_event())
                        if transcient:
                            await wait((transcient, get), return_when=FIRST_COMPLETED)
                            if not transcient.done():
                                with timeit("transcient"):
                                    await cancel(transcient)
                            transcient = None

                        sync, method, params = await get
                        task = step(method, params=params)
                        if sync:
                            with timeit(method):
                                await task
                        else:
                            transcient = create_task(task)
            finally:
                await cancel(
                    *(get or loop.create_future(), transcient or loop.create_future())
                )

        async def c2() -> None:
            t1, has_drawn = monotonic(), False

            @_die
            async def cont() -> None:
                nonlocal has_drawn
                with suppress_and_log():
                    if state := state_ref.val:
                        for attempt in range(1, RENDER_RETRIES + 1):
                            try:
                                derived = await redraw(state, focus=focus_ref.val)
                            except NvimError as e:
                                if attempt == RENDER_RETRIES:
                                    log.warning("%s", e)
                            else:
                                state_ref.val = replace(
                                    state, node_row_lookup=derived.node_row_lookup
                                )
                                focus_ref.val = None
                                break

                        if settings.profiling and not has_drawn:
                            has_drawn = True
                            await _profile(t1=t1)

            while True:
                await event.wait()
                try:

                    create_task(cont())
                finally:
                    event.clear()

        await gather(c1(), c2(), _sched(state_ref))


async def init(socket: ServerAddr, ppid: int, th: ThreadPoolExecutor) -> None:
    loop = get_running_loop()
    loop.set_default_executor(th)
    log.setLevel(DEBUG_LVL if DEBUG else INFO)

    die: Future = Future()

    async def cont() -> None:
        async with conn(die, socket=socket, default=_default) as client:
            await _go(loop, client=client)

    await gather(wrap_future(die), cont())
