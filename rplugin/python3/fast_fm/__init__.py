from asyncio import run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
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

        self.lock = Lock()
        self.chan = ThreadPoolExecutor(max_workers=1)
        self.nvim = nvim
        self.state = initial_state(settings)
        self.settings = settings

        keys(self.nvim, self.settings)

    def _update(self, state: State) -> None:
        with self.lock:
            self.state = state

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
                    self._update(ret)

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

        state = c_primary(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMsecondary")
    def secondary(self, args: Sequence[Any]) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        state = c_secondary(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMresize")
    def resize(self, args: Sequence[Any]) -> None:
        pass

    @function("FMrefresh")
    def refresh(self, args: Sequence[Any]) -> None:
        """
        Redraw buffers
        """

        state = c_refresh(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMcollapse")
    def collapse(self, args: Sequence[Any]) -> None:
        """
        Collapse folder
        """

        state = c_collapse(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMhidden")
    def hidden(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        state = c_hidden(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMfollow")
    def follow(self, args: Sequence[Any]) -> None:
        """
        Toggle hidden
        """

        state = c_follow(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

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

        state = c_new(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMrename")
    def rename(self, args: Sequence[Any]) -> None:
        """
        rename file / folder
        """

        state = c_rename(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMclear")
    def clear(self, args: Sequence[Any]) -> None:
        """
        Clear selected
        """

        state = c_clear(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMselect")
    def select(self, args: Sequence[Any]) -> None:
        """
        Folder / File -> select
        """
        visual, *_ = args
        is_visual = visual == 1

        state = c_select(
            self.nvim, state=self.state, settings=self.settings, is_visual=is_visual
        )
        self._update(state)

    @function("FMdelete")
    def delete(self, args: Sequence[Any]) -> None:
        """
        Delete selected
        """

        state = c_delete(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMcut")
    def cut(self, args: Sequence[Any]) -> None:
        """
        Cut selected
        """

        state = c_cut(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

    @function("FMcopy")
    def copy(self, args: Sequence[Any]) -> None:
        """
        Copy selected
        """

        state = c_copy(self.nvim, state=self.state, settings=self.settings)
        self._update(state)

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

        state = a_on_bufenter(
            self.nvim, state=self.state, settings=self.settings, buf=int(buf)
        )
        self._update(state)
