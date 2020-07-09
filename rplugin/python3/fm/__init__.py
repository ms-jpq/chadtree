from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable

from pynvim import Nvim, autocmd, command, function, plugin

from .state import initial
from .wm import toggle


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.chan = ThreadPoolExecutor(max_workers=1)
        self.nvim = nvim
        self.state = initial()

    def _submit(self, coro: Awaitable[None]) -> None:
        """
        Work around for coroutine deadlocks
        """
        loop = get_event_loop()

        def stage() -> None:
            fut = run_coroutine_threadsafe(coro, loop)
            fut.result()

        self.chan.submit(stage)

    @command("FMOpen")
    def fm_open(self, *args) -> None:
        toggle(self.nvim)

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

    @autocmd("BufEnter", pattern="neovimasyncfm")
    def on_bufenter(self) -> None:
        async def commit() -> None:
            self.nvim.out_write(str(self.state) + "\n")

        self._submit(commit())
