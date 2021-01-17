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
    ext_colours = gen_hl(FM_HL_PREFIX, mapping=github_colours)

    if use_ls_colours:
        lsc = parse_lsc()
        _ext_colours = ext_colours
        _mode_pre = lsc.mode_pre
        _mode_post = lsc.mode_post
        _ext_lookup = lsc.exts
        _name_exact: Mapping[str, HLgroup] = {}
        _name_glob = lsc.name_glob
    else:
        ext_lookup = _trans_inverse(light_theme, mapping=nerd_colours.type)
        name_exact = _trans_inverse(light_theme, mapping=nerd_colours.name_exact)
        name_glob = _trans_inverse(light_theme, mapping=nerd_colours.name_glob)
        _ext_colours = ext_colours
        _mode_pre = {}
        _mode_post = {}
        _ext_lookup = ext_lookup
        _name_exact = name_exact
        _name_glob = name_glob

    groups = tuple(
        chain(
            _ext_colours.values(),
            _mode_pre.values(),
            _mode_post.values(),
            _ext_lookup.values(),
            _name_exact.values(),
            _name_glob.values(),
        ),
    )

    context = HLcontext(
        groups=groups,
        ext_colours=_trans(_ext_colours),
        mode_pre=_trans(_mode_pre),
        mode_post=_trans(_mode_post),
        ext_lookup=_trans(_ext_lookup),
        name_exact=_trans(_name_exact),
        name_glob=_trans(_name_glob),
        particular_mappings=particular_mappings,
    )
    return context
