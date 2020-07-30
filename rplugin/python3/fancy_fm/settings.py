from typing import Any

from .consts import config_json, ignore_json, view_json
from .da import load_json, merge
from .ls_colours import parse_ls_colours
from .types import IconSet, Settings, UpdateTime, VersionControlOptions


def initial(user_config: Any, user_icons: Any, user_ignores: Any) -> Settings:
    config = merge(load_json(config_json), user_config)
    icon_c = merge(load_json(view_json), user_icons)
    ignore = merge(load_json(ignore_json), user_ignores)

    use_icons = config["use_icons"]
    icon_cs = icon_c["unicode"] if use_icons else icon_c["ascii"]

    icons = IconSet(
        active=icon_cs["status"]["active"],
        selected=icon_cs["status"]["selected"],
        folder_open=icon_cs["folder"]["open"],
        folder_closed=icon_cs["folder"]["closed"],
        link=icon_cs["link"]["normal"],
        link_broken=icon_cs["link"]["broken"],
        filetype=icon_c["files"]["type"],
        filename=icon_c["files"]["name"],
        quickfix_hl=icon_c["highlights"]["quickfix"],
        version_ctl_hl=icon_c["highlights"]["version_control"],
    )

    update = UpdateTime(
        min_time=config["update_time"]["min"], max_time=config["update_time"]["max"]
    )

    version_ctl = VersionControlOptions(defer=config["version_control"]["defer"])
    hl_context = parse_ls_colours()

    settings = Settings(
        follow=config["follow"],
        icons=icons,
        hl_context=hl_context,
        keymap=config["keymap"],
        name_ignore=ignore["name"],
        open_left=config["open_left"],
        path_ignore=ignore["path"],
        session=config["session"],
        show_hidden=config["show_hidden"],
        update=update,
        use_icons=use_icons,
        version_ctl=version_ctl,
        width=config["width"],
    )

    return settings
