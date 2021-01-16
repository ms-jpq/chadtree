from typing import Iterator, Mapping, Tuple
from uuid import uuid4

from pynvim_pp.highlight import HLgroup

from ..consts import FM_HL_PREFIX

LEGAL_CTERM = {
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
            name = f"{FM_HL_PREFIX}_{name_prefix}_{uuid4().hex}"
            yield key, HLgroup(name=name, guifg=val)

    return {k: v for k, v in cont()}
