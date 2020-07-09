from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor

from pynvim import Nvim, autocmd, command, plugin


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.pool = ThreadPoolExecutor()
        self.nvim = nvim

    @command("FMOPEN")
    def fm_open(self, *args) -> None:
        self.nvim.current.line = "OWO"

    @autocmd("BufEnter", pattern="*")
    def on_bufenter(self) -> None:
        def commit() -> None:
            self.nvim.out_write("reeeeeeeeeeee" + "\n")

        loop = get_event_loop()
        loop.call_soon(commit)
