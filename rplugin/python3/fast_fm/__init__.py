from asyncio import AbstractEventLoop, Event, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Any, Awaitable, Optional, Sequence, cast

from pynvim import Nvim, command, function, plugin

from .commands import (
    a_on_filetype,
    c_clear,
    c_collapse,
    c_copy,
    c_copy_name,
    c_cut,
    c_delete,
    c_follow,
    c_hidden,
    c_new,
    c_open,
    c_primary,
    c_quit,
    c_refresh,
    c_rename,
    c_secondary,
    c_select,
)
from .consts import fm_filetype
from .nvim import Nvim2, autocmd, print
from .schedule import schedule
from .settings import initial as initial_settings
from .state import initial as initial_state
from .types import State


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        user_config = nvim.vars.get("fast_fm_settings", None)
        user_icons = nvim.vars.get("fast_fm_icons", None)
        user_ignores = nvim.vars.get("fast_fm_ignores", None)
        self.settings = initial_settings(
            user_config=user_config, user_icons=user_icons, user_ignores=user_ignores
        )
        self.state = cast(State, None)

        self.chan = ThreadPoolExecutor(max_workers=1)
        self.ch = Event()
        self.nvim1 = nvim
        self.nvim = Nvim2(nvim)

        self._initialized = False

    def _submit(self, co: Awaitable[Optional[State]], wait: bool = True) -> None:
        loop: AbstractEventLoop = self.nvim1.loop

        def run(nvim: Nvim) -> None:
            fut = run_coroutine_threadsafe(co, loop)
            try:
                ret = fut.result()
            except Exception as e:
                stack = format_exc()
                nvim.async_call(nvim.err_write, f"{stack}{e}\n")
            else:

                def cont() -> None:
                    if ret:
                        self.state = ret

                loop.call_soon_threadsafe(cont)

        if wait:
            self.chan.submit(run, self.nvim1)
        else:
            run_coroutine_threadsafe(co, loop)

    def _run(self, fn: Any, *args: Any, **kwargs: Any) -> None:
        async def run() -> Optional[State]:
            if not self.state:
                self.state = await initial_state(self.settings)

            return await fn(
                self.nvim, state=self.state, settings=self.settings, *args, **kwargs
            )

        self._submit(run())

    def _initialize(self) -> None:
        async def setup() -> None:
            await autocmd(
                self.nvim,
                events=("FileType",),
                filters=(fm_filetype,),
                fn="_FMkeybind",
                arg_eval=("expand('<abuf>')",),
            )

            await autocmd(
                self.nvim,
                events=("BufWritePost", "FocusGained"),
                fn="FMscheduleupdate",
            )

        async def cycle() -> None:
            update = self.settings.update
            async for _ in schedule(
                self.ch, min_time=update.min_time, max_time=update.max_time,
            ):
                state = await c_refresh(
                    self.nvim, state=self.state, settings=self.settings
                )
                self.state = state

        async def forever() -> None:
            while True:
                try:
                    await cycle()
                except Exception as e:
                    await print(self.nvim, e, error=True)

        if self._initialized:
            return
        else:
            self._initialized = True
            self._submit(setup())
            self._submit(forever(), wait=False)

    @command("FMopen")
    def fm_open(self, *args: Any, **kwargs: Any) -> None:
        """
        Toggle sidebar
        """

        self._initialize()
        self._run(c_open)

    @function("FMscheduleupdate")
    def schedule_udpate(self, args: Sequence[Any]) -> None:
        self.ch.set()

    @function("_FMkeybind")
    def on_filetype(self, args: Sequence[Any]) -> None:
        """
        Setup keybind
        """
        buf, *_ = args
        bufnr = int(buf)

        self._run(a_on_filetype, bufnr=bufnr)

    @function("FMquit")
    def fm_quit(self, args: Sequence[Any]) -> None:
        """
        Close sidebar
        """

        self._run(c_quit)

    @function("FMprimary")
    def primary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open
        """

        self._run(c_primary)

    @function("FMsecondary")
    def secondary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        self._run(c_secondary)

    @function("FMresize")
    def resize(self, args: Sequence[Any]) -> None:
        pass

    @function("FMrefresh")
    def refresh(self, args: Sequence[Any]) -> None:
        """
        Redraw buffers
        """

        self._run(c_refresh)

    @function("FMcollapse")
    def collapse(self, args: Sequence[Any]) -> None:
        """
        Collapse folder
        """

        self._run(c_collapse)

    @function("FMhidden")
    def hidden(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        self._run(c_hidden)

    @function("FMfollow")
    def follow(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        self._run(c_follow)

    @function("FMcopyname")
    def copy_name(self, args: Sequence[Any]) -> None:
        """
        Copy dirname / filename
        """
        visual, *_ = args
        is_visual = visual == 1

        self._run(c_copy_name, is_visual=is_visual)

    @function("FMnew")
    def new(self, args: Sequence[Any]) -> None:
        """
        new file / folder
        """

        self._run(c_new)

    @function("FMrename")
    def rename(self, args: Sequence[Any]) -> None:
        """
        rename file / folder
        """

        self._run(c_rename)

    @function("FMclear")
    def clear(self, args: Sequence[Any]) -> None:
        """
        Clear selected
        """

        self._run(c_clear)

    @function("FMselect")
    def select(self, args: Sequence[Any]) -> None:
        """
        Folder / File -> select
        """
        visual, *_ = args
        is_visual = visual == 1

        self._run(c_select, is_visual=is_visual)

    @function("FMdelete")
    def delete(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """

        self._run(c_delete)

    @function("FMcut")
    def cut(self, args: Sequence[Any]) -> None:
        """
        Cut selected
        """

        self._run(c_cut)

    @function("FMcopy")
    def copy(self, args: Sequence[Any]) -> None:
        """
        Copy selected
        """

        self._run(c_copy)
