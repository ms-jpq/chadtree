from .nvim import Buffer, Nvim2
from .types import Settings


async def keymap(nvim: Nvim2, buffer: Buffer, settings: Settings) -> None:
    options = {"noremap": True, "silent": True, "expr": True}

    for function, mappings in settings.keymap.items():
        for mapping in mappings:
            for mode in ("n", "v"):
                await nvim.api.buf_set_keymap(
                    buffer, mode, mapping, f"{function}()", options
                )
