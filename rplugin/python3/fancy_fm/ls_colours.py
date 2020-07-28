from os import environ


def parse_ls_colours() -> None:
    colours = environ.get("LS_COLORS", "")
    lookup = {
        k: v
        for k, _, v in (
            segment.partition("=") for segment in colours.strip(":").split(":")
        )
    }

    normal = lookup.pop("no", None)
    file = lookup.pop("fi", None)
    directory = lookup.pop("di", None)
    link = lookup.pop("ln", None)
    pipe = lookup.pop("pi", None)
    block_device = lookup.pop("bd", None)
    char_device = lookup.pop("cd", None)
    orphan_link = lookup.pop("or", None)
    socket = lookup.pop("so", None)
    executable = lookup.pop("ex", None)
    sticky_dir = lookup.pop("st", None)
    door = lookup.pop("do", None)
    sticky_writable = lookup.pop("tw", None)
    other_writable = lookup.pop("ow", None)
    set_uid = lookup.pop("su", None)
    multi_hardlink = lookup.pop("mh", None)
    file_w_capacity = lookup.pop("ca", None)
    set_gid = lookup.pop("sg", None)
    _unknown = lookup.pop("rs", None)

    special = (
        normal,
        file,
        multi_hardlink,
        directory,
        file_w_capacity,
        sticky_writable,
        other_writable,
        link,
        pipe,
        block_device,
        set_gid,
        char_device,
        set_uid,
        orphan_link,
        socket,
        executable,
        sticky_dir,
        door,
        _unknown,
    )
    exts = tuple(key for key in lookup if key.startswith("*"))
    ext_lookup = {key[:]: lookup.pop(key) for key in exts}
