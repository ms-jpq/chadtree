from asyncio import AbstractEventLoop, Event, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from operator import add, sub
from os import linesep
from traceback import format_exc
from typing import Any, Awaitable, Callable, Optional, Sequence

from pynvim import Nvim, command, function, plugin

from .highlight import add_hl_groups
from .nvim import autocmd, run_forever
from .scheduler import schedule
from .settings import initial as initial_settings
from .state import initial as initial_state
from .transitions import (
    a_changedir,
    a_follow,
    a_quickfix,
    a_session,
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
    c_open_system,
    c_primary,
    c_quit,
    c_refresh,
    c_rename,
    c_resize,
    c_secondary,
    c_select,
    redraw,
)
from .types import State


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        user_config = nvim.vars.get("fancy_fm_settings", {})
        user_view = nvim.vars.get("fancy_fm_view", {})
        user_icons = nvim.vars.get("fancy_fm_icons", {})
        user_ignores = nvim.vars.get("fancy_fm_ignores", {})
        self.settings = initial_settings(
            user_config=user_config,
            user_view=user_view,
            user_icons=user_icons,
            user_ignores=user_ignores,
        )
        self.state: Optional[State] = None

        self.chan = ThreadPoolExecutor(max_workers=1)
        self.ch = Event()
        self.nvim = nvim

        self._initialized = False

    def _submit(self, co: Awaitable[None]) -> None:
        loop: AbstractEventLoop = self.nvim.loop

        def run(nvim: Nvim) -> None:
            fut = run_coroutine_threadsafe(co, loop)
            try:
                fut.result()
            except Exception as e:
                stack = format_exc()
                nvim.async_call(nvim.err_write, f"{stack}{e}{linesep}")

        self.chan.submit(run, self.nvim)

    async def _curr_state(self) -> State:
        if not self.state:
            self.state = await initial_state(self.nvim, settings=self.settings)

        return self.state

    def _run(
        self, fn: Callable[..., Awaitable[Optional[State]]], *args: Any, **kwargs: Any
    ) -> None:
        async def run() -> None:
            state = await self._curr_state()
            new_state = await fn(
                self.nvim, state=state, settings=self.settings, *args, **kwargs
            )
            if new_state:
                self.state = new_state
                await redraw(self.nvim, state=new_state)

        self._submit(run())

    def _initialize(self) -> None:
        async def setup() -> None:
            await autocmd(
                self.nvim, events=("DirChanged",), fn="_FMchange_dir",
            )

            await autocmd(
                self.nvim, events=("BufEnter",), fn="_FMfollow",
            )

            await autocmd(
                self.nvim,
                events=("BufWritePost", "FocusGained"),
                fn="FMschedule_update",
            )

            await autocmd(self.nvim, events=("FocusLost", "ExitPre"), fn="_FMsession")

            await autocmd(self.nvim, events=("QuickfixCmdPost",), fn="_FMquickfix")

            groups = chain(
                self.settings.hl_context.groups, self.settings.icons.ext_colours
            )
            await add_hl_groups(self.nvim, groups=groups)

        if self._initialized:
            return
        else:
            self._initialized = True
            self._submit(setup())
            run_forever(self.nvim, self._ooda_loop)

    async def _ooda_loop(self) -> None:
        update = self.settings.update
        async for elapsed in schedule(
            self.ch, min_time=update.min_time, max_time=update.max_time,
        ):
            state = await self._curr_state()
            new_state = await c_refresh(self.nvim, state=state, settings=self.settings)
            self.state = new_state
            await redraw(self.nvim, state=new_state)

    @command("FMopen")
    def fm_open(self, *args: Any, **kwargs: Any) -> None:
        """
        Toggle sidebar
        """

        self._initialize()
        self._run(c_open)

    @function("FMschedule_update")
    def schedule_udpate(self, args: Sequence[Any]) -> None:
        """
        Follow directory
        """

        self.ch.set()

    @function("_FMchange_dir")
    def on_changedir(self, args: Sequence[Any]) -> None:
        """
        Follow files
        """

        self._run(a_changedir)

    @function("_FMfollow")
    def on_bufenter(self, args: Sequence[Any]) -> None:
        """
        Follow buffer
        """

        self._run(a_follow)

    @function("_FMsession")
    def on_leave(self, args: Sequence[Any]) -> None:
        """
        Follow buffer
        """

        self._run(a_session)

    @function("_FMquickfix")
    def on_quickfix(self, args: Sequence[Any]) -> None:
        """
        Update quickfix list
        """

        self._run(a_quickfix)

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

    @function("FMbigger")
    def bigger(self, args: Sequence[Any]) -> None:
        """
        Bigger sidebar
        """

        self._run(c_resize, direction=add)

    @function("FMsmaller")
    def smaller(self, args: Sequence[Any]) -> None:
        """
        Smaller sidebar
        """

        self._run(c_resize, direction=sub)

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
        Toggle follow
        """

        self._run(c_follow)

    @function("FMcopy_name")
    def copy_name(self, args: Sequence[Any]) -> None:
        """
        Copy dirname / filename
        """
        is_visual, *_ = args

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
        is_visual, *_ = args

        self._run(c_select, is_visual=is_visual)

    @function("FMdelete")
    def delete(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """
        is_visual, *_ = args

        self._run(c_delete, is_visual=is_visual)

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

    @function("FMopen_sys")
    def open_sys(self, args: Sequence[Any]) -> None:
        """
        Open using finder / dolphin, etc
        """

        self._run(c_open_system)
