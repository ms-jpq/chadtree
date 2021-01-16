from itertools import chain
from typing import Mapping, TypeVar

from pynvim_pp.highlight import HLgroup

from .ls_colours import parse_lsc
from .types import HLcontext, UserHLGroups

T = TypeVar("T")


def _trans(mapping: Mapping[T, HLgroup]) -> Mapping[T, str]:
    return {k: v.name for k, v in mapping.items()}


def parse_colours(
    use_ls_colours: bool,
    particular_mappings: UserHLGroups,
    ext_colours: Mapping[str, HLgroup],
    ext_lookup: Mapping[str, HLgroup],
    name_exact: Mapping[str, HLgroup],
    name_glob: Mapping[str, HLgroup],
) -> HLcontext:
    if use_ls_colours:
        lsc = parse_lsc()
        _ext_colours = lsc.exts
        _mode_pre = lsc.mode_pre
        _mode_post = lsc.mode_post
        _ext_lookup = {}
        _name_exact = {}
        _name_glob = lsc.name_glob
    else:
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
