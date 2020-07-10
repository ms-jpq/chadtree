from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable

from pynvim import Nvim, autocmd, command, function, plugin

from .consts import fm_filetype
from .keymap import keymap
from .settings import initial as initial_settings
from .state import initial as initial_state
from .wm import toggle_shown


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

    def _print(self, message: str, error: bool = False) -> None:
        write = self.nvim.err_write if error else self.nvim.out_write
        write(message)
        write("\n")

    @command("FMOpen")
    def fm_open(self, *args) -> None:
        toggle_shown(self.nvim)

    @function("FMsettings")
    def settings(self, settings: Any) -> None:
        """
        Settings update
        """
        pass

    @function("FMprimary")
    def primary(self) -> None:
        """
        Folders -> toggle
        File -> open
        """
        pass

    @function("FMsecondary")
    def secondary(self) -> None:
        """
        Folders -> toggle
        File -> preview
        """
        pass

    @function("FMhidden")
    def hidden(self) -> None:
        """
        Toggle hidden
        """
        pass

    @function("FMnew")
    def new(self) -> None:
        """
        new file / folder
        """
        pass

    @function("FMrename")
    def rename(self) -> None:
        """
        rename file / folder
        """
        pass

    @function("FMselect")
    def select(self) -> None:
        """
        Folder / File -> select
        """
        pass

    @function("FMclear")
    def clear(self) -> None:
        """
        Clear selected
        """
        pass

    @function("FMdelete")
    def delete(self) -> None:
        """
        Delete selected
        """
        pass

    @function("FMcut")
    def cut(self) -> None:
        """
        Cut selected
        """
        pass

    @function("FMcopy")
    def copy(self) -> None:
        """
        Copy selected
        """
        pass

    @function("FMpaste")
    def paste(self) -> None:
        """
        Paste selected
        """
        pass

    @function("FMcopyname")
    def copyname(self) -> None:
        """
        Copy dirname / filename
        """
        pass

    @autocmd("BufEnter", pattern=fm_filetype)
    def on_bufenter(self) -> None:
        """
        Setup keybind
        """
        keymap(self.nvim, settings=self.settings)
