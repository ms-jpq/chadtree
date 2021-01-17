from itertools import chain
from typing import Callable, Mapping, TypeVar, cast

from pynvim_pp.highlight import HLgroup
from std2.coloursys import hex_inverse
from std2.functools import identity

from ..consts import FM_HL_PREFIX
from .highlight import gen_hl
from .ls_colours import parse_lsc
from .types import GithubColours, HLcontext, NerdColours, UserHLGroups

T = TypeVar("T")


def _trans(mapping: Mapping[T, HLgroup]) -> Mapping[T, str]:
    return {k: v.name for k, v in mapping.items()}


def _trans_inverse(inverse: bool, mapping: Mapping[str, str]) -> Mapping[str, HLgroup]:
    trans = hex_inverse if inverse else cast(Callable[[str], str], identity)
    return gen_hl(
        FM_HL_PREFIX, mapping={key: trans(val) for key, val in mapping.items()}
    )


def parse_colours(
    use_ls_colours: bool,
    light_theme: bool,
    particular_mappings: UserHLGroups,
    github_colours: GithubColours,
    nerd_colours: NerdColours,
) -> HLcontext:
    github_exts = gen_hl(FM_HL_PREFIX, mapping=github_colours)

    if use_ls_colours:
        lsc = parse_lsc()
        mode_pre = lsc.mode_pre
        mode_post = lsc.mode_post
        ext_exact = lsc.exts
        name_exact: Mapping[str, HLgroup] = {}
        name_glob = lsc.name_glob
    else:
        mode_pre = {}
        mode_post = {}
        ext_exact = _trans_inverse(light_theme, mapping=nerd_colours.type)
        name_exact = _trans_inverse(light_theme, mapping=nerd_colours.name_exact)
        name_glob = _trans_inverse(light_theme, mapping=nerd_colours.name_glob)

    groups = tuple(
        chain(
            github_exts.values(),
            mode_pre.values(),
            mode_post.values(),
            ext_exact.values(),
            name_exact.values(),
            name_glob.values(),
        ),
    )

    context = HLcontext(
        groups=groups,
        icon_exts=_trans(github_exts),
        mode_pre=_trans(mode_pre),
        mode_post=_trans(mode_post),
        ext_exact=_trans(ext_exact),
        name_exact=_trans(name_exact),
        name_glob=_trans(name_glob),
        particular_mappings=particular_mappings,
    )
    return context
