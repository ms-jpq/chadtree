from typing import Any, Dict, cast

from .consts import (
    colours_json,
    config_json,
    custom_colours_json,
    icon_lookup,
    ignore_json,
    view_json,
)
from .da import load_json, merge
from .highlight import gen_hl
from .ls_colours import parse_ls_colours
from .types import (
    ColourMapping,
    Colours,
    MimetypeOptions,
    Settings,
    Sortby,
    UpdateTime,
    VersionControlOptions,
    ViewOptions,
)


def initial(
    user_config: Any, user_view: Any, user_ignores: Any, user_colours: Any
) -> Settings:
    config = merge(load_json(config_json), user_config, replace=True)
    view = merge(load_json(view_json), user_view, replace=True)
    icons_json = icon_lookup[config["use_icons"]]
    icon_c = cast(Any, load_json(icons_json))
    ignore = merge(load_json(ignore_json), user_ignores, replace=True)
    github_colours = cast(Dict[str, str], load_json(colours_json))
    colours_c = merge(cast(Any, load_json(custom_colours_json)), user_colours)

    use_icons = config["use_icons"]

    bit8_mapping = {
        key: ColourMapping(hl8=val["hl8"], hl24=val["hl24"])
        for key, val in colours_c["8_bit"].items()
    }
    ext_colours = gen_hl("github", mapping=github_colours)
    colours = Colours(bit8_mapping=bit8_mapping, exts=ext_colours)
    icons = ViewOptions(
        active=icon_c["status"]["active"],
        default_icon=icon_c["default_icon"],
        colours=colours,
        filename_exact=icon_c["name_exact"],
        filename_glob=icon_c["name_glob"],
        filetype=icon_c["type"],
        folder_closed=icon_c["folder"]["closed"],
        folder_open=icon_c["folder"]["open"],
        link=icon_c["link"]["normal"],
        link_broken=icon_c["link"]["broken"],
        quickfix_hl=view["highlights"]["quickfix"],
        selected=icon_c["status"]["selected"],
        time_fmt=view["time_format"],
        version_ctl_hl=view["highlights"]["version_control"],
    )

    update = UpdateTime(
        min_time=config["update_time"]["min"], max_time=config["update_time"]["max"]
    )

    version_ctl = VersionControlOptions(
        defer=config["version_control"]["defer"],
        enable=config["version_control"]["enable"],
    )
    hl_context = parse_ls_colours(colours)

    keymap = {f"CHAD{k}": v for k, v in config["keymap"].items()}
    mime = MimetypeOptions(
        warn={*config["mimetypes"]["warn"]},
        ignore_exts={*config["mimetypes"]["ignore_exts"]},
    )

    sortby = tuple(Sortby[sb] for sb in config["sort_by"])
    settings = Settings(
        follow=config["follow"],
        hl_context=hl_context,
        icons=icons,
        keymap=keymap,
        lang=config["lang"],
        logging_level=config["logging_level"],
        mime=mime,
        name_ignore=ignore["name"],
        open_left=config["open_left"],
        path_ignore=ignore["path"],
        session=config["session"],
        show_hidden=config["show_hidden"],
        sort_by=sortby,
        update=update,
        use_icons=use_icons,
        version_ctl=version_ctl,
        width=config["width"],
        win_local_opts=view["window_options"],
    )

    return settings
