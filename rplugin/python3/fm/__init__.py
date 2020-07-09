from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable

from pynvim import Nvim, autocmd, command, function, plugin

from .state import initial


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
        async def commit() -> None:
            self.nvim.current.line = "OWO"

        self._submit(commit())

    @function("FMprimary")
    def primary() -> None:
        """
        Folders -> toggle
        File -> open
        """
        pass

    @function("FMsecondary")
    def secondary() -> None:
        """
        Folders -> toggle
        File -> preview
        """
        pass

    @function("FMrename")
    def rename() -> None:
        """
        rename file / folder
        """
        pass

    @function("FMselect")
    def select() -> None:
        """
        Folder / File -> select
        """
        pass

    @function("FMclear")
    def clear() -> None:
        """
        Clear selected
        """
        pass

    @function("FMdelete")
    def delete() -> None:
        """
        Delete selected
        """
        pass

    @function("FMcut")
    def cut() -> None:
        """
        Cut selected
        """
        pass

    @function("FMcopy")
    def copy() -> None:
        """
        Copy selected
        """
        pass

    @function("FMpaste")
    def paste() -> None:
        """
        Paste selected
        """
        pass

    @autocmd("BufEnter", pattern="*")
    def on_bufenter(self) -> None:
        async def commit() -> None:
            self.nvim.out_write(str(self.state) + "\n")

        self._submit(commit())
