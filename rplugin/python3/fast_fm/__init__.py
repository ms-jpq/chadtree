from asyncio import run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Any, Awaitable, Optional, Sequence

from pynvim import Nvim, autocmd, function, plugin

from .commands import (
    a_on_bufenter,
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
    c_refresh,
    c_rename,
    c_secondary,
    c_select,
)
from .consts import fm_filetype
from .keymap import keys
from .nvim import print
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
        self.nvim = nvim
        self.state = initial_state(settings)
        self.settings = settings

        keys(self.nvim, self.settings)

    def _submit(self, coro: Awaitable[Optional[State]]) -> None:
        loop = self.nvim.loop

        def run() -> None:
            fut = run_coroutine_threadsafe(coro, loop)
            try:
                ret = fut.result()
            except Exception as e:
                stack = format_exc()
                self.nvim.async_call(print, self.nvim, f"{stack}{e}", error=True)
            else:
                if ret:
                    self.state = ret

        self.chan.submit(run)

    @function("FMopen")
    def fm_open(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open
        """

        c_open(self.nvim, state=self.state, settings=self.settings)

    @function("FMprimary")
    def primary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> open
        """

        self.state = c_primary(self.nvim, state=self.state, settings=self.settings)

    @function("FMsecondary")
    def secondary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        self.state = c_secondary(self.nvim, state=self.state, settings=self.settings)

    @function("FMresize")
    def resize(self, args: Sequence[Any]) -> None:
        pass

    @function("FMrefresh")
    def refresh(self, args: Sequence[Any]) -> None:
        """
        Redraw buffers
        """

        self.state = c_refresh(self.nvim, state=self.state, settings=self.settings)

    @function("FMcollapse")
    def collapse(self, args: Sequence[Any]) -> None:
        """
        Collapse folder
        """

        self.state = c_collapse(self.nvim, state=self.state, settings=self.settings)

    @function("FMhidden")
    def hidden(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        self.state = c_hidden(self.nvim, state=self.state, settings=self.settings)

    @function("FMfollow")
    def follow(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        self.state = c_follow(self.nvim, state=self.state, settings=self.settings)

    @function("FMcopyname")
    def copy_name(self, args: Sequence[Any]) -> None:
        """
        Copy dirname / filename
        """

        c_copy_name(self.nvim, state=self.state, settings=self.settings)

    @function("FMnew")
    def new(self, args: Sequence[Any]) -> None:
        """
        new file / folder
        """

        self.state = c_new(self.nvim, state=self.state, settings=self.settings)

    @function("FMrename")
    def rename(self, args: Sequence[Any]) -> None:
        """
        rename file / folder
        """

        self.state = c_rename(self.nvim, state=self.state, settings=self.settings)

    @function("FMclear")
    def clear(self, args: Sequence[Any]) -> None:
        """
        Clear selected
        """

        self.state = c_clear(self.nvim, state=self.state, settings=self.settings)

    @function("FMselect")
    def select(self, args: Sequence[Any]) -> None:
        """
        Folder / File -> select
        """
        visual, *_ = args
        is_visual = visual == 1

        self.state = c_select(
            self.nvim, state=self.state, settings=self.settings, is_visual=is_visual
        )

    @function("FMdelete")
    def delete(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """

        self.state = c_delete(self.nvim, state=self.state, settings=self.settings)

    @function("FMcut")
    def cut(self, args: Sequence[Any]) -> None:
        """
        Cut selected
        """

        self.state = c_cut(self.nvim, state=self.state, settings=self.settings)

    @function("FMcopy")
    def copy(self, args: Sequence[Any]) -> None:
        """
        Copy selected
        """

        self.state = c_copy(self.nvim, state=self.state, settings=self.settings)

    @autocmd("FileType", pattern=fm_filetype, eval="expand('<abuf>')")
    def on_filetype(self, buf: str) -> None:
        """
        Setup keybind
        """

        a_on_filetype(self.nvim, state=self.state, settings=self.settings, buf=int(buf))

    @autocmd("BufEnter", eval="expand('<abuf>')")
    def on_bufenter(self, buf: str) -> None:
        """
        Update background tasks
        """

        self.state = a_on_bufenter(
            self.nvim, state=self.state, settings=self.settings, buf=int(buf)
        )
