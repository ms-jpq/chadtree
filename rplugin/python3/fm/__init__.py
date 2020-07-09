from asyncio import get_running_loop
from pynvim import Nvim, autocmd, command, plugin

from .consts import icons_json, ignore_json
from .da import load_json


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim
        self.icons = load_json(icons_json)
        self.ignored = load_json(ignore_json)

    @command("FMOPEN")
    def fm_open(self, *args) -> None:
        self.nvim.current.line = "OWO"

    @autocmd("BufEnter", pattern="*")
    def on_bufenter(self) -> None:
        async def commit() -> None:
            filename = self.nvim.funcs.bufname()
            self.nvim.out_write("testplugin is in " + str(filename) + "\n")

        # loop = get_running_loop()
        # fut = loop.create_task(commit())
        # fut.result()
