from pynvim import Nvim

from .nvim import Buffer
from .types import Settings


def remap(lhs: str, rhs: str) -> None:
    pass


def keymap(nvim: Nvim, buffer: Buffer, settings: Settings) -> None:
    pass
