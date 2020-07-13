from pynvim import Nvim

from .nvim import Buffer, Nvim2
from .types import Settings

_options = {"noremap": True, "silent": True, "nowait": True}


def keys(nvim: Nvim, settings: Settings) -> None:
    for function, mappings in settings.keymap.entire.items():
        for mapping in mappings:
            nvim.api.set_keymap("n", mapping, f"<cmd>call {function}(0)<cr>", _options)


async def keymap(nvim: Nvim2, buffer: Buffer, settings: Settings) -> None:

    for function, mappings in settings.keymap.buffer.items():
        for mapping in mappings:
            await nvim.api.buf_set_keymap(
                buffer, "n", mapping, f"<cmd>call {function}(0)<cr>", _options
            )
            await nvim.api.buf_set_keymap(
                buffer, "v", mapping, f"<esc><cmd>call {function}(1)<cr>", _options
            )
