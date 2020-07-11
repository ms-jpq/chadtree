from .nvim import Buffer, Nvim
from .types import Settings

_options = {"noremap": True, "silent": True, "expr": True}


def keys(nvim: Nvim, settings: Settings) -> None:
    for function, mappings in settings.keymap.entire.items():
        for mapping in mappings:
            nvim.api.set_keymap("n", mapping, f"{function}()", _options)


def keymap(nvim: Nvim, buffer: Buffer, settings: Settings) -> None:

    for function, mappings in settings.keymap.buffer.items():
        for mapping in mappings:
            for mode in ("n", "v"):
                nvim.api.buf_set_keymap(
                    buffer, mode, mapping, f"{function}()", _options
                )
