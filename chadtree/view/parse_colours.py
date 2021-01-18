from itertools import chain
from json import loads
from os import environ
from typing import Mapping, TypeVar

from pynvim.api.nvim import Nvim
from pynvim_pp.highlight import HLgroup
from std2.pickle import decode
from std2.types import never

from ..consts import (
    FM_HL_PREFIX,
    GITHUB_COLOURS_JSON,
    NERD_COLOURS_DARK_JSON,
    NERD_COLOURS_LIGHT_JSON,
)
from .highlight import gen_hl
from .ls_colours import parse_lsc
from .types import ColourChoice, GithubColours, HLcontext, NerdColours, UserHLGroups

T = TypeVar("T")


def _trans(mapping: Mapping[T, HLgroup]) -> Mapping[T, str]:
    return {k: v.name for k, v in mapping.items()}


def load_colours(
    nvim: Nvim,
    colours: ColourChoice,
    particular_mappings: UserHLGroups,
) -> HLcontext:
    ls_colours = environ.get("LS_COLORS", "")
    if not ls_colours:
        colours = ColourChoice.nerd_tree

    github_colours: GithubColours = decode(
        GithubColours, loads(GITHUB_COLOURS_JSON.read_text())
    )

    if colours is ColourChoice.ls_colours:
        lsc = parse_lsc(ls_colours)
        mode_pre = lsc.mode_pre
        mode_post = lsc.mode_post
        ext_exact = lsc.exts
        name_exact: Mapping[str, HLgroup] = {}
        name_glob = lsc.name_glob
    elif colours is ColourChoice.nerd_tree:
        light_theme = nvim.options["background"] == "light"
        target = NERD_COLOURS_LIGHT_JSON if light_theme else NERD_COLOURS_DARK_JSON
        nerd_colours: NerdColours = decode(NerdColours, loads(target.read_text()))
        mode_pre = {}
        mode_post = {}
        ext_exact = gen_hl(FM_HL_PREFIX, mapping=nerd_colours.ext_exact)
        name_exact = gen_hl(FM_HL_PREFIX, mapping=nerd_colours.name_exact)
        name_glob = gen_hl(FM_HL_PREFIX, mapping=nerd_colours.name_glob)
    else:
        never(colours)

    icon_exts = gen_hl(FM_HL_PREFIX, mapping=github_colours)

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
    return context
