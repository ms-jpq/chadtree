from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable

from pynvim import Nvim, autocmd, command, function, plugin

from .consts import fm_filetype
from .keymap import keymap
from .nvim import Buffer
from .settings import initial as initial_settings
from .state import initial as initial_state
from .wm import is_fm_buffer, toggle_shown


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.chan = ThreadPoolExecutor(max_workers=1)
        self.nvim = nvim
        settings = initial_settings()
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

    @command("FMOpen")
    def fm_open(self, *args) -> None:
        toggle_shown(self.nvim, settings=self.settings)

    @function("FMsettings")
    def settings(self, settings: Any) -> None:
        """
        Settings update
        """

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

    @function("FMredraw")
    def redraw(self) -> None:
        """
        Redraw buffer
        """

    @function("FMhidden")
    def hidden(self) -> None:
        """
        Toggle hidden
        """

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
