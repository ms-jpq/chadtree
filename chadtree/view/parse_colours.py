def _trans(mapping: Mapping[T, HLgroup]) -> Mapping[T, str]:
    return {k: v.name for k, v in mapping.items()}

def parse_ls_colours(
    use_ls_colours: bool,
    particular_mappings: UserHLGroups,
    ext_colours: Mapping[str, HLgroup],
    ext_lookup: Mapping[str, HLgroup],
    name_exact: Mapping[str, HLgroup],
    name_glob: Mapping[str, HLgroup],
) -> HLcontext:
    ls_colours = environ.get("LS_COLORS", "")
    hl_lookup: MutableMapping[str, HLgroup] = {
        k: _parseHLGroup(_parse_styling(v))
        for k, _, v in (
            segment.partition("=") for segment in ls_colours.strip(":").split(":")
        )
    }

    mode_pre: Mapping[Mode, HLgroup] = {
        k: v
        for k, v in ((v, hl_lookup.pop(k, None)) for k, v in _SPECIAL_PRE_TABLE.items())
        if v
    }

    mode_post: Mapping[Optional[Mode], HLgroup] = {
        k: v
        for k, v in (
            (v, hl_lookup.pop(k, None)) for k, v in _SPECIAL_POST_TABLE.items()
        )
        if v
    }

    ext_keys = tuple(
        key for key in hl_lookup if key.startswith("*.") and key.count(".") == 1
    )
    _ext_lookup: Mapping[str, HLgroup] = {
        key[1:]: hl_lookup.pop(key) for key in ext_keys
    }
    _name_exact = {**name_exact, **hl_lookup}
    __ext_lookup = {**ext_lookup, **_ext_lookup}

    groups = tuple(
        chain(
            ext_colours.values(),
            mode_pre.values(),
            mode_post.values(),
            __ext_lookup.values(),
            _name_exact.values(),
            name_glob.values(),
        )
    )

    context = HLcontext(
        groups=groups,
        ext_colours=_trans(ext_colours),
        mode_pre=_trans(mode_pre),
        mode_post=_trans(mode_post),
        ext_lookup=_trans(__ext_lookup),
        name_exact=_trans(_name_exact),
        name_glob=_trans(name_glob),
        particular_mappings=particular_mappings,
    )
    return context

