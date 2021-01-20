from itertools import chain
from os import environ
from typing import Mapping, Tuple, TypeVar

from chad_types import (
    Artifact,
    Icons,
    IconColourSetEnum,
    IconSetEnum,
    LSColoursEnum,
    TextColourSetEnum,
)
from pynvim.api.nvim import Nvim
from pynvim_pp.highlight import HLgroup
from std2.types import never

from ..consts import FM_HL_PREFIX
from .highlight import gen_hl
from .ls_colours import parse_lsc
from .types import HLcontext, HLGroups

T = TypeVar("T")


def _trans(mapping: Mapping[T, HLgroup]) -> Mapping[T, str]:
    return {k: v.name for k, v in mapping.items()}


def load_theme(
    nvim: Nvim,
    artifact: Artifact,
    particular_mappings: HLGroups,
    ls_colours: LSColoursEnum,
    icon_set: IconSetEnum,
    icon_colour_set: IconColourSetEnum,
    text_colour_set: TextColourSetEnum,
) -> Tuple[Icons, HLcontext]:

    if icon_set is IconSetEnum.ascii:
        icons = artifact.icons.ascii
    elif icon_set is IconSetEnum.devicons:
        icons = artifact.icons.devicons
    elif icon_set is IconSetEnum.emoji:
        icons = artifact.icons.emoji
    else:
        never(icon_set)

    if ls_colours is LSColoursEnum.env:
        _lsc = environ.get("LS_COLORS", "")
    elif ls_colours is LSColoursEnum.dark_256:
        _lsc = artifact.ls_colours.dark_256
    elif ls_colours is LSColoursEnum.ansi_light:
        _lsc = artifact.ls_colours.ansi_light
    elif ls_colours is LSColoursEnum.ansi_dark:
        _lsc = artifact.ls_colours.ansi_dark
    elif ls_colours is LSColoursEnum.ansi_universal:
        _lsc = artifact.ls_colours.ansi_universal
    elif ls_colours is LSColoursEnum.none:
        _lsc = ""
    else:
        never(ls_colours)

    if _lsc:
        lsc = parse_lsc(_lsc)
        mode_pre = lsc.mode_pre
        mode_post = lsc.mode_post
        ext_exact = lsc.exts
        name_exact: Mapping[str, HLgroup] = {}
        name_glob = lsc.name_glob
    else:
        if text_colour_set is TextColourSetEnum.nerdtree_syntax_light:
            text_colour = artifact.text_colours.nerdtree_syntax_light
        elif text_colour_set is TextColourSetEnum.nerdtree_syntax_dark:
            text_colour = artifact.text_colours.nerdtree_syntax_dark
        else:
            never(text_colour_set)

        mode_pre = {}
        mode_post = {}
        ext_exact = gen_hl(FM_HL_PREFIX, mapping=text_colour.ext_exact)
        name_exact = gen_hl(FM_HL_PREFIX, mapping=text_colour.name_exact)
        name_glob = gen_hl(FM_HL_PREFIX, mapping=text_colour.name_glob)

    icon_exts = gen_hl(FM_HL_PREFIX, mapping=artifact.icon_colours.github)

    groups = tuple(
        chain(
            icon_exts.values(),
            mode_pre.values(),
            mode_post.values(),
            ext_exact.values(),
            name_exact.values(),
            name_glob.values(),
        ),
    )

    context = HLcontext(
        groups=groups,
        icon_exts=_trans(icon_exts),
        mode_pre=_trans(mode_pre),
        mode_post=_trans(mode_post),
        ext_exact=_trans(ext_exact),
        name_exact=_trans(name_exact),
        name_glob=_trans(name_glob),
        particular_mappings=particular_mappings,
    )

    return icons, context
