from dataclasses import dataclass, field
from os import linesep
from typing import Iterator, Optional, Set

from pynvim import Nvim

from .nvim import call

LEGAL_CTERM: Set[str] = {
    "bold",
    "underline",
    "undercurl",
    "strikethrough",
    "reverse",
    "italic",
    "standout",
}

LEGAL_CTERM_COLOURS = range(8)


@dataclass(frozen=True)
class HLgroup:
    name: str
    cterm: Set[str] = field(default_factory=set)
    ctermfg: Optional[str] = None
    ctermbg: Optional[str] = None
    guifg: Optional[str] = None
    guibg: Optional[str] = None


async def add_hl_groups(nvim: Nvim, groups: Iterator[HLgroup]) -> None:
    def parse() -> Iterator[str]:
        for group in groups:
            assert group.cterm <= LEGAL_CTERM
            name = group.name
            _cterm = ",".join(group.cterm)
            cterm = f"cterm={_cterm}"
            ctermfg = f"ctermfg={group.ctermfg}" if group.ctermfg else ""
            ctermbg = f"ctermbg={group.ctermbg}" if group.ctermbg else ""
            guifg = f"guifg={group.guifg}" if group.guifg else ""
            guibg = f"guibg={group.guibg}" if group.guibg else ""

            yield f"highlight {name} {cterm} {ctermfg} {ctermbg} {guifg} {guibg}"

    def cont() -> None:
        commands = linesep.join(parse())
        nvim.api.exec(commands, False)

    await call(nvim, cont)
