from typing import Iterator, Mapping, Set, Tuple
from uuid import uuid4

from pynvim_pp.highlight import HLgroup

from .consts import fm_hl_prefix

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


def gen_hl(name_prefix: str, mapping: Mapping[str, str]) -> Mapping[str, HLgroup]:
    def cont() -> Iterator[Tuple[str, HLgroup]]:
        for key, val in mapping.items():
            name = f"{fm_hl_prefix}_{name_prefix}_{uuid4().hex}"
            yield key, HLgroup(name=name, guifg=val)

    return {k: v for k, v in cont()}
