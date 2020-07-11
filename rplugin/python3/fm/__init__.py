from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable, Optional

from pynvim import Nvim, autocmd, command, function, plugin

from .consts import fm_filetype
from .git import status
from .keymap import keymap
from .nvim import Buffer, Window, print
from .settings import initial as initial_settings
from .state import index
from .state import initial as initial_state
from .types import GitStatus
from .wm import is_fm_buffer, toggle_shown, update_buffers


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
        self.git_status = GitStatus()

    def _submit(self, coro: Awaitable[None]) -> None:
        """
        Work around for coroutine deadlocks
        """
        loop = get_event_loop()

        def stage() -> None:
            fut = run_coroutine_threadsafe(coro, loop)
            fut.result()

        self.chan.submit(stage)

    def index(self) -> Optional[str]:
        window: Window = self.nvim.current.window
        row, _ = self.nvim.api.win_get_cursor(window)
        row = row - 1
        return index(self.state, row)

    def redraw(self) -> None:
        lines = self.state.rendered
        update_buffers(self.nvim, lines=lines)

    @command("FMOpen")
    def fm_open(self, *_) -> None:
        toggle_shown(self.nvim, settings=self.settings)
        self.redraw()

    @function("FMprimary")
    def primary(self, *_) -> None:
        """
        Folders -> toggle
        File -> open
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMsecondary")
    def secondary(self, *_) -> None:
        """
        Folders -> toggle
        File -> preview
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMrefresh")
    def refresh(self, *_) -> None:
        """
        Redraw buffers
        """

        async def cont() -> None:
            self.git_status = await status()
            self.redraw()

        self._submit(cont())

    @function("FMhidden")
    def hidden(self, *_) -> None:
        """
        Toggle hidden
        """

        self.redraw()

    @function("FMnew")
    def new(self, *_) -> None:
        """
        new file / folder
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMrename")
    def rename(self, *_) -> None:
        """
        rename file / folder
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMselect")
    def select(self, *_) -> None:
        """
        Folder / File -> select
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMclear")
    def clear(self, *_) -> None:
        """
        Clear selected
        """

        self.redraw()

    @function("FMdelete")
    def delete(self, *_) -> None:
        """
        Delete selected
        """

        self.redraw()

    @function("FMcut")
    def cut(self, *_) -> None:
        """
        Cut selected
        """

        self.redraw()

    @function("FMcopy")
    def copy(self, *_) -> None:
        """
        Copy selected
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMpaste")
    def paste(self, *_) -> None:
        """
        Paste selected
        """

        path = self.index()
        if path:
            self.redraw()

    @function("FMcopyname")
    def copyname(self, *_) -> None:
        """
        Copy dirname / filename
        """

        path = self.index()
        if path:
            self.nvim.funcs.setreg("+", path)
            self.nvim.funcs.setreg("*", path)
            print(self.nvim, f"📎 {path}")

    @autocmd("FileType", pattern=fm_filetype, eval="expand('<abuf>')")
    def on_filetype(self, buf: str) -> None:
        """
        Setup keybind
        """

        buffer: Buffer = self.nvim.buffers[int(buf)]
        keymap(self.nvim, buffer=buffer, settings=self.settings)

    @autocmd("BufEnter", eval="expand('<abuf>')")
    def on_bufenter(self, buf: str) -> None:
        """
        Update git
        """

        async def cont() -> None:
            self.git_status = await status()

        buffer: Buffer = self.nvim.buffers[int(buf)]
        if is_fm_buffer(self.nvim, buffer=buffer):
            self._submit(cont())

    @autocmd("FocusGained")
    def on_focus(self) -> None:
        """
        Update git
        """

        async def cont() -> None:
            self.git_status = await status()
            self.redraw()

        self._submit(cont())
