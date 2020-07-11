from .nvim import Buffer, Nvim2
from .types import Settings

_options = {"noremap": True, "silent": True, "expr": True}


async def keys(nvim: Nvim2, settings: Settings) -> None:
    for function, mappings in settings.keymap.entire.items():
        for mapping in mappings:
            await nvim.api.set_keymap("n", mapping, f"{function}()", _options)


async def keymap(nvim: Nvim2, buffer: Buffer, settings: Settings) -> None:

    for function, mappings in settings.keymap.buffer.items():
        for mapping in mappings:
            for mode in ("n", "v"):
                await nvim.api.buf_set_keymap(
                    buffer, mode, mapping, f"{function}()", _options
                )
