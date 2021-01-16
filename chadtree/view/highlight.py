from typing import Iterator, Mapping, Tuple
from uuid import uuid4

from pynvim_pp.atomic import Atomic
from pynvim_pp.highlight import HLgroup, highlight

from ..consts import FM_HL_PREFIX
from .types import HLcontext

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


def hl_instructions(ctx: HLcontext) -> Atomic:
    return highlight(
        *ctx.github_exts.values(),
        *ctx.ext_lookup.values(),
        *ctx.mode_lookup_pre.values(),
        *ctx.mode_lookup_post.values(),
        *ctx.name_lookup.values(),
    )
