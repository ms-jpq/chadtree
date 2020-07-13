from asyncio import AbstractEventLoop, Event, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Any, Awaitable, Optional, Sequence

from pynvim import Nvim, autocmd, function, plugin

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
from .keymap import keys
from .nvim import Nvim2, print
from .schedule import schedule
from .settings import initial as initial_settings
from .state import initial as initial_state
from .types import State


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        user_settings = nvim.vars.get("fm_settings", None)
        user_icons = nvim.vars.get("fm_icons", None)
        settings = initial_settings(user_settings=user_settings, user_icons=user_icons)

        self.chan = ThreadPoolExecutor(max_workers=1)
        self.ch = Event()
        self.nvim1 = nvim
        self.nvim = Nvim2(nvim)
        self.state = initial_state(settings)
        self.settings = settings

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

    @autocmd("VimEnter")
    def stub(self) -> None:
        async def setup() -> None:
            await keys(self.nvim, settings=self.settings)
            await print(self.nvim, "FM loaded 🍎")

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

        self._submit(setup())
        self._submit(forever(), wait=False)

    @function("FMasyncupdate")
    def async_udpate(self, args: Sequence[Any]) -> None:
        self.ch.set()

    @autocmd("FileType", pattern=fm_filetype, eval="expand('<abuf>')")
    def on_filetype(self, buf: str) -> None:
        """
        Setup keybind
        """

        co = a_on_filetype(
            self.nvim, state=self.state, settings=self.settings, buf=int(buf)
        )
        self._submit(co)

    @function("FMquit")
    def fm_quit(self, args: Sequence[Any]) -> None:
        """
        Close sidebar
        """

        co = c_quit(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMopen")
    def fm_open(self, args: Sequence[Any]) -> None:
        """
        Toggle sidebar
        """

        co = c_open(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMprimary")
    def primary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open
        """

        co = c_primary(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMsecondary")
    def secondary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        co = c_secondary(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMresize")
    def resize(self, args: Sequence[Any]) -> None:
        pass

    @function("FMrefresh")
    def refresh(self, args: Sequence[Any]) -> None:
        """
        Redraw buffers
        """

        co = c_refresh(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMcollapse")
    def collapse(self, args: Sequence[Any]) -> None:
        """
        Collapse folder
        """

        co = c_collapse(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMhidden")
    def hidden(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        co = c_hidden(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMfollow")
    def follow(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        co = c_follow(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMcopyname")
    def copy_name(self, args: Sequence[Any]) -> None:
        """
        Copy dirname / filename
        """
        visual, *_ = args
        is_visual = visual == 1

        co = c_copy_name(
            self.nvim, state=self.state, settings=self.settings, is_visual=is_visual
        )
        self._submit(co)

    @function("FMnew")
    def new(self, args: Sequence[Any]) -> None:
        """
        new file / folder
        """

        co = c_new(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMrename")
    def rename(self, args: Sequence[Any]) -> None:
        """
        rename file / folder
        """

        co = c_rename(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMclear")
    def clear(self, args: Sequence[Any]) -> None:
        """
        Clear selected
        """

        co = c_clear(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMselect")
    def select(self, args: Sequence[Any]) -> None:
        """
        Folder / File -> select
        """
        visual, *_ = args
        is_visual = visual == 1

        co = c_select(
            self.nvim, state=self.state, settings=self.settings, is_visual=is_visual
        )
        self._submit(co)

    @function("FMdelete")
    def delete(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """

        co = c_delete(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMcut")
    def cut(self, args: Sequence[Any]) -> None:
        """
        Cut selected
        """

        co = c_cut(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)

    @function("FMcopy")
    def copy(self, args: Sequence[Any]) -> None:
        """
        Copy selected
        """

        co = c_copy(self.nvim, state=self.state, settings=self.settings)
        self._submit(co)
