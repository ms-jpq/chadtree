from pynvim import Nvim

from .nvim import Buffer
from .types import Settings


def keymap(nvim: Nvim, buffer: Buffer, settings: Settings) -> None:
    options = {"noremap": True, "silent": True, "expr": True}

    for function, mappings in settings.keymap.items():
        for mapping in mappings:
            nvim.api.buf_set_keymap(buffer, "n", mapping, f"{function}()", options)
