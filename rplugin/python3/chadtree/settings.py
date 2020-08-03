from typing import Any, Dict, cast

from .consts import colours_json, config_json, icons_json, ignore_json, view_json
from .da import load_json, merge
from .highlight import gen_hl
from .ls_colours import parse_ls_colours
from .types import (
    MimetypeOptions,
    Settings,
    UpdateTime,
    VersionControlOptions,
    ViewOptions,
)


def initial(user_config: Any, user_view: Any, user_ignores: Any) -> Settings:
    config = merge(load_json(config_json), user_config, replace=True)
    view = merge(load_json(view_json), user_view, replace=True)
    icon_c = cast(Any, load_json(icons_json))
    ignore = merge(load_json(ignore_json), user_ignores, replace=True)
    colours = cast(Dict[str, str], load_json(colours_json))

    use_icons = config["use_icons"]
    view_c = view["unicode"] if use_icons else view["ascii"]

    ext_colours = gen_hl("github", mapping=colours)
    icons = ViewOptions(
        active=view_c["status"]["active"],
        default_icon=view_c["default_icon"],
        ext_colours=ext_colours,
        filename_exact=icon_c["name_exact"],
        filename_glob=icon_c["name_glob"],
        filetype=icon_c["type"],
        folder_closed=view_c["folder"]["closed"],
        folder_open=view_c["folder"]["open"],
        link=view_c["link"]["normal"],
        link_broken=view_c["link"]["broken"],
        quickfix_hl=view["highlights"]["quickfix"],
        selected=view_c["status"]["selected"],
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
    hl_context = parse_ls_colours()

    keymap = {f"CHAD{k}": v for k, v in config["keymap"].items()}
    mime = MimetypeOptions(
        warn={*config["mimetypes"]["warn"]},
        ignore_exts={*config["mimetypes"]["ignore_exts"]},
    )

    settings = Settings(
        follow=config["follow"],
        hl_context=hl_context,
        icons=icons,
        keymap=keymap,
        name_ignore=ignore["name"],
        open_left=config["open_left"],
        path_ignore=ignore["path"],
        session=config["session"],
        show_hidden=config["show_hidden"],
        update=update,
        use_icons=use_icons,
        version_ctl=version_ctl,
        mime=mime,
        width=config["width"],
    )

    return settings
