from asyncio import (
    AbstractEventLoop,
    Event,
    Lock,
    create_task,
    run_coroutine_threadsafe,
)
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from operator import add, sub
from os import linesep
from traceback import format_exc
from typing import Any, Awaitable, Callable, Optional, Sequence

from pynvim import Nvim, command, function, plugin
from pynvim.api.common import NvimError

from .highlight import add_hl_groups
from .nvim import autocmd, print, run_forever
from .scheduler import schedule
from .settings import initial as initial_settings
from .state import initial as initial_state
from .transitions import (
    a_changedir,
    a_follow,
    a_quickfix,
    a_session,
    c_change_focus,
    c_change_focus_up,
    c_clear_filter,
    c_clear_selection,
    c_click,
    c_collapse,
    c_copy,
    c_copy_name,
    c_cut,
    c_delete,
    c_new_filter,
    c_toggle_follow,
    c_hidden,
    c_new,
    c_open,
    c_open_system,
    c_quit,
    c_refresh,
    c_rename,
    c_resize,
    c_select,
    c_stat,
    c_toggle_vc,
    c_trash,
    redraw,
)
from .types import ClickType, Settings, State


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        user_config = nvim.vars.get("chadtree_settings", {})
        user_view = nvim.vars.get("chadtree_view", {})
        user_ignores = nvim.vars.get("chadtree_ignores", {})
        self.settings = initial_settings(
            user_config=user_config, user_view=user_view, user_ignores=user_ignores,
        )
        self.state: Optional[State] = None

        self.chan = ThreadPoolExecutor(max_workers=1)
        self.ch = Event()
        self.lock = Lock()
        self.nvim = nvim

        self._init = create_task(self._initialize())
        run_forever(self.nvim, self._ooda_loop)

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
            async with self.lock:
                await self._init
                state = await self._curr_state()
                new_state = await fn(
                    self.nvim, state=state, settings=self.settings, *args, **kwargs
                )
                if new_state:
                    self.state = new_state
                    await redraw(self.nvim, state=new_state)

        self._submit(run())

    async def _initialize(self) -> None:
        await autocmd(
            self.nvim, events=("DirChanged",), fn="_CHADchange_dir",
        )

        await autocmd(
            self.nvim, events=("BufEnter",), fn="_CHADfollow",
        )

        await autocmd(
            self.nvim, events=("BufWritePost", "FocusGained"), fn="CHADschedule_update",
        )

        await autocmd(self.nvim, events=("FocusLost", "ExitPre"), fn="_CHADsession")

        await autocmd(self.nvim, events=("QuickfixCmdPost",), fn="_CHADquickfix")

        groups = chain(
            self.settings.hl_context.groups, self.settings.icons.ext_colours.values(),
        )
        await add_hl_groups(self.nvim, groups=groups)

    async def _ooda_loop(self) -> None:
        update = self.settings.update
        async for elapsed in schedule(
            self.ch, min_time=update.min_time, max_time=update.max_time,
        ):
            async with self.lock:
                state = await self._curr_state()
                try:
                    new_state = await c_refresh(
                        self.nvim, state=state, settings=self.settings
                    )
                    self.state = new_state
                    await redraw(self.nvim, state=new_state)
                except NvimError:
                    self.ch.set()

    @command("CHADopen")
    def fm_open(self, *args: Any, **kwargs: Any) -> None:
        """
        Toggle sidebar
        """

        self._run(c_open)

    @function("CHADschedule_update")
    def schedule_udpate(self, args: Sequence[Any]) -> None:
        """
        Follow directory
        """

        self.ch.set()

    @function("_CHADchange_dir")
    def on_changedir(self, args: Sequence[Any]) -> None:
        """
        Follow files
        """

        self._run(a_changedir)

    @function("_CHADfollow")
    def on_bufenter(self, args: Sequence[Any]) -> None:
        """
        Follow buffer
        """

        self._run(a_follow)

    @function("_CHADsession")
    def on_leave(self, args: Sequence[Any]) -> None:
        """
        Follow buffer
        """

        self._run(a_session)

    @function("_CHADquickfix")
    def on_quickfix(self, args: Sequence[Any]) -> None:
        """
        Update quickfix list
        """

        self._run(a_quickfix)

    @function("CHADquit")
    def quit(self, args: Sequence[Any]) -> None:
        """
        Close sidebar
        """

        self._run(c_quit)

    @function("CHADchange_focus")
    def change_focus(self, args: Sequence[Any]) -> None:
        """
        Refocus root directory
        """

        self._run(c_change_focus)

    @function("CHADchange_focus_up")
    def change_focus_up(self, args: Sequence[Any]) -> None:
        """
        Refocus root directory up
        """

        self._run(c_change_focus_up)

    @function("CHADrefocus")
    def refocus(self, args: Sequence[Any]) -> None:
        """
        Refocus root directory to cwd
        """

        self._run(a_changedir)

    @function("CHADstat")
    def stat(self, args: Sequence[Any]) -> None:
        """
        Print file stat to cmdline
        """

        self._run(c_stat)

    @function("CHADprimary")
    def primary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open
        """

        self._run(c_click, click_type=ClickType.primary)

    @function("CHADsecondary")
    def secondary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        self._run(c_click, click_type=ClickType.secondary)

    @function("CHADtertiary")
    def tertiary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open in new tab
        """

        self._run(c_click, click_type=ClickType.tertiary)

    @function("CHADv_split")
    def v_split(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open in vertical split
        """

        self._run(c_click, click_type=ClickType.v_split)

    @function("CHADh_split")
    def h_split(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open in horizontal split
        """

        self._run(c_click, click_type=ClickType.h_split)

    @function("CHADbigger")
    def bigger(self, args: Sequence[Any]) -> None:
        """
        Bigger sidebar
        """

        self._run(c_resize, direction=add)

    @function("CHADsmaller")
    def smaller(self, args: Sequence[Any]) -> None:
        """
        Smaller sidebar
        """

        self._run(c_resize, direction=sub)

    @function("CHADrefresh")
    def refresh(self, args: Sequence[Any]) -> None:
        """
        Redraw buffers
        """

        async def cont(nvim: Nvim, state: State, settings: Settings) -> None:
            await print(nvim, "⏳...⌛️")
            await c_refresh(nvim, state=state, settings=settings)
            await print(nvim, "✅")

        self._run(cont)

    @function("CHADcollapse")
    def collapse(self, args: Sequence[Any]) -> None:
        """
        Collapse folder
        """

        self._run(c_collapse)

    @function("CHADtoggle_hidden")
    def hidden(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        self._run(c_hidden)

    @function("CHADtoggle_follow")
    def toggle_follow(self, args: Sequence[Any]) -> None:
        """
        Toggle follow
        """

        self._run(c_toggle_follow)

    @function("CHADtoggle_version_control")
    def toggle_vc(self, args: Sequence[Any]) -> None:
        """
        Toggle version control
        """

        self._run(c_toggle_vc)

    @function("CHADfilter")
    def filter_pattern(self, args: Sequence[Any]) -> None:
        """
        Update filter
        """

        self._run(c_new_filter)

    @function("CHADcopy_name")
    def copy_name(self, args: Sequence[Any]) -> None:
        """
        Copy dirname / filename
        """
        is_visual, *_ = args

        self._run(c_copy_name, is_visual=is_visual)

    @function("CHADnew")
    def new(self, args: Sequence[Any]) -> None:
        """
        new file / folder
        """

        self._run(c_new)

    @function("CHADrename")
    def rename(self, args: Sequence[Any]) -> None:
        """
        rename file / folder
        """

        self._run(c_rename)

    @function("CHADclear_selection")
    def clear_selection(self, args: Sequence[Any]) -> None:
        """
        Clear selected
        """

        self._run(c_clear_selection)

    @function("CHADclear_filter")
    def clear_filter(self, args: Sequence[Any]) -> None:
        """
        Clear selected
        """

        self._run(c_clear_filter)

    @function("CHADselect")
    def select(self, args: Sequence[Any]) -> None:
        """
        Folder / File -> select
        """
        is_visual, *_ = args

        self._run(c_select, is_visual=is_visual)

    @function("CHADdelete")
    def delete(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """
        is_visual, *_ = args

        self._run(c_delete, is_visual=is_visual)

    @function("CHADtrash")
    def trash(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """
        is_visual, *_ = args

        self._run(c_trash, is_visual=is_visual)

    @function("CHADcut")
    def cut(self, args: Sequence[Any]) -> None:
        """
        Cut selected
        """

        self._run(c_cut)

    @function("CHADcopy")
    def copy(self, args: Sequence[Any]) -> None:
        """
        Copy selected
        """

        self._run(c_copy)

    @function("CHADopen_sys")
    def open_sys(self, args: Sequence[Any]) -> None:
        """
        Open using finder / dolphin, etc
        """

        self._run(c_open_system)
