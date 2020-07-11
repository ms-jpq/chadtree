from asyncio import get_running_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from traceback import format_exc
from typing import Awaitable, Optional

from pynvim import Nvim, autocmd, function, plugin

from .commands import (
    a_on_bufenter,
    a_on_filetype,
    a_on_focus,
    c_clear,
    c_copy,
    c_copy_name,
    c_cut,
    c_delete,
    c_hidden,
    c_new,
    c_open,
    c_paste,
    c_primary,
    c_refresh,
    c_rename,
    c_secondary,
    c_select,
)
from .consts import fm_filetype
from .keymap import keys
from .nvim import Nvim2
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
        self.nvim1 = nvim
        self.nvim2 = Nvim2(nvim)
        self.state = initial_state(settings)
        self.settings = settings

        self.schedule(keys(self.nvim2, self.settings))

    # Work around for coroutine deadlocks
    def schedule(self, coro: Awaitable[Optional[State]]) -> None:
        loop = get_running_loop()

        async def wrapped(nvim1: Nvim) -> Optional[State]:
            try:
                return await coro
            except Exception as e:
                stack = format_exc()
                msg = f"error caught while executing async callback:\n{stack}\n{e}"
                nvim1.async_call(nvim1.err_write, msg)
                return None

        def stage() -> None:
            fut = run_coroutine_threadsafe(wrapped(self.nvim1), loop)
            state = fut.result()
            if state:
                self.state = state

        self.chan.submit(stage)

    @function("FMopen")
    def fm_open(self, *_) -> None:
        """
        Folders -> toggle
        File -> open
        """

        self.schedule(c_open(self.nvim2, state=self.state, settings=self.settings))

    @function("FMprimary")
    def primary(self, *_) -> None:
        """
        Folders -> toggle
        File -> open
        """

        self.schedule(c_primary(self.nvim2, state=self.state))

    @function("FMsecondary")
    def secondary(self, *_) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        self.schedule(c_secondary(self.nvim2, state=self.state))

    @function("FMrefresh")
    def refresh(self, *_) -> None:
        """
        Redraw buffers
        """

        self.schedule(c_refresh(self.nvim2, state=self.state))

    @function("FMhidden")
    def hidden(self, *_) -> None:
        """
        Toggle hidden
        """

        self.schedule(c_hidden(self.nvim2, state=self.state))

    @function("FMcopyname")
    def copy_name(self, *_) -> None:
        """
        Copy dirname / filename
        """

        self.schedule(c_copy_name(self.nvim2, state=self.state))

    @function("FMnew")
    def new(self, *_) -> None:
        """
        new file / folder
        """

        self.schedule(c_new(self.nvim2, state=self.state))

    @function("FMrename")
    def rename(self, *_) -> None:
        """
        rename file / folder
        """

        self.schedule(c_rename(self.nvim2, state=self.state))

    @function("FMselect")
    def select(self, *_) -> None:
        """
        Folder / File -> select
        """

        self.schedule(c_select(self.nvim2, state=self.state))

    @function("FMclear")
    def clear(self, *_) -> None:
        """
        Clear selected
        """

        self.schedule(c_clear(self.nvim2, state=self.state))

    @function("FMdelete")
    def delete(self, *_) -> None:
        """
        Delete selected
        """

        self.schedule(c_delete(self.nvim2, state=self.state))

    @function("FMcut")
    def cut(self, *_) -> None:
        """
        Cut selected
        """

        self.schedule(c_cut(self.nvim2, state=self.state))

    @function("FMcopy")
    def copy(self, *_) -> None:
        """
        Copy selected
        """

        self.schedule(c_copy(self.nvim2, state=self.state))

    @function("FMpaste")
    def paste(self, *_) -> None:
        """
        Paste selected
        """

        self.schedule(c_paste(self.nvim2, state=self.state))

    @autocmd("FileType", pattern=fm_filetype, eval="expand('<abuf>')")
    def on_filetype(self, buf: str) -> None:
        """
        Setup keybind
        """

        self.schedule(
            a_on_filetype(
                self.nvim2, state=self.state, settings=self.settings, buf=int(buf)
            )
        )

    @autocmd("BufEnter", eval="expand('<abuf>')")
    def on_bufenter(self, buf: str) -> None:
        """
        Update git
        """

        self.schedule(a_on_bufenter(self.nvim2, state=self.state, buf=int(buf)))

    @autocmd("FocusGained")
    def on_focus(self) -> None:
        """
        Update git
        """

        self.schedule(a_on_focus(self.nvim2, state=self.state))
