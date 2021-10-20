from itertools import chain
from os import environ
from typing import Mapping, Tuple, TypeVar, Union

from pynvim_pp.highlight import HLgroup
from std2.types import never

from chad_types import (
    Artifact,
    IconColourSetEnum,
    IconGlyphs,
    IconGlyphSetEnum,
    LSColoursEnum,
    TextColourSetEnum,
)

from ..consts import FM_HL_PREFIX
from .highlight import gen_hl
from .ls_colours import parse_lsc
from .types import HLcontext, HLGroups

T = TypeVar("T")


def _trans(mapping: Mapping[T, HLgroup]) -> Mapping[T, str]:
    return {k: v.name for k, v in mapping.items()}


def load_theme(
    artifact: Artifact,
    particular_mappings: HLGroups,
    discrete_colours: Mapping[str, str],
    icon_set: IconGlyphSetEnum,
    icon_colour_set: IconColourSetEnum,
    text_colour_set: Union[LSColoursEnum, TextColourSetEnum],
) -> Tuple[IconGlyphs, HLcontext]:

    if icon_set is IconGlyphSetEnum.ascii:
        icons = artifact.icons.ascii
    elif icon_set is IconGlyphSetEnum.devicons:
        icons = artifact.icons.devicons
    elif icon_set is IconGlyphSetEnum.emoji:
        icons = artifact.icons.emoji
    else:
        never(icon_set)

    if text_colour_set is LSColoursEnum.env and "LS_COLORS" not in environ:
        text_colour_set = LSColoursEnum.solarized_dark_256

    if isinstance(text_colour_set, LSColoursEnum):
        if text_colour_set is LSColoursEnum.env:
            _lsc = environ.get("LS_COLORS", "")
        elif text_colour_set is LSColoursEnum.solarized_dark_256:
            _lsc = artifact.ls_colours.solarized_dark_256
        elif text_colour_set is LSColoursEnum.solarized_light:
            _lsc = artifact.ls_colours.solarized_light
        elif text_colour_set is LSColoursEnum.solarized_dark:
            _lsc = artifact.ls_colours.solarized_dark
        elif text_colour_set is LSColoursEnum.solarized_universal:
            _lsc = artifact.ls_colours.solarized_universal
        elif text_colour_set is LSColoursEnum.nord:
            _lsc = artifact.ls_colours.nord
        elif text_colour_set is LSColoursEnum.trapdoor:
            _lsc = artifact.ls_colours.trapdoor
        else:
            never(text_colour_set)

        lsc = parse_lsc(_lsc, discrete_colours=discrete_colours)
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

    if icon_colour_set is IconColourSetEnum.github:
        icon_exts = gen_hl(FM_HL_PREFIX, mapping=artifact.icon_colours.github)
    elif icon_colour_set is IconColourSetEnum.none:
        icon_exts = gen_hl(FM_HL_PREFIX, mapping={})
    else:
        never(icon_colour_set)

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
