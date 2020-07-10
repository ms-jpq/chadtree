from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable

from pynvim import Nvim, autocmd, command, function, plugin

from .consts import fm_filetype
from .keymap import keymap
from .nvim import Buffer, Window
from .settings import initial as initial_settings
from .state import initial as initial_state
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

    def _submit(self, coro: Awaitable[None]) -> None:
        """
        Work around for coroutine deadlocks
        """
        loop = get_event_loop()

        def stage() -> None:
            fut = run_coroutine_threadsafe(coro, loop)
            fut.result()

        self.chan.submit(stage)

    def print(self, message: str, error: bool = False) -> None:
        write = self.nvim.err_write if error else self.nvim.out_write
        write(message)
        write("\n")

    def index(self) -> None:
        window: Window = self.nvim.current.window
        row, _ = self.nvim.api.win_get_cursor(window)
        row = row - 1

    def redraw(self) -> None:
        lines = self.state.rendered
        update_buffers(self.nvim, lines=lines)

    @command("FMOpen")
    def fm_open(self, *args) -> None:
        toggle_shown(self.nvim, settings=self.settings)
        self.redraw()

    @function("FMprimary")
    def primary(self) -> None:
        """
        Folders -> toggle
        File -> open
        """

    @function("FMsecondary")
    def secondary(self) -> None:
        """
        Folders -> toggle
        File -> preview
        """

    @function("FMrefresh")
    def refresh(self) -> None:
        """
        Redraw buffer
        """

    @function("FMhidden")
    def hidden(self) -> None:
        """
        Toggle hidden
        """
        self.redraw()

    @function("FMnew")
    def new(self) -> None:
        """
        new file / folder
        """

    @function("FMrename")
    def rename(self) -> None:
        """
        rename file / folder
        """

    @function("FMselect")
    def select(self) -> None:
        """
        Folder / File -> select
        """

    @function("FMclear")
    def clear(self) -> None:
        """
        Clear selected
        """

    @function("FMdelete")
    def delete(self) -> None:
        """
        Delete selected
        """

    @function("FMcut")
    def cut(self) -> None:
        """
        Cut selected
        """

    @function("FMcopy")
    def copy(self) -> None:
        """
        Copy selected
        """

    @function("FMpaste")
    def paste(self) -> None:
        """
        Paste selected
        """

    @function("FMcopyname")
    def copyname(self) -> None:
        """
        Copy dirname / filename
        """

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
        buffer: Buffer = self.nvim.buffers[int(buf)]
        if is_fm_buffer(self.nvim, buffer=buffer):
            pass

    @autocmd("FocusGained")
    def on_focus(self) -> None:
        """
        Update git
        """
