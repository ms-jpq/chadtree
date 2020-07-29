from typing import Any

from .consts import config_json, icons_json, ignore_json
from .da import load_json, merge
from .ls_colours import parse_ls_colours
from .types import IconSet, Settings, UpdateTime, VersionControlOptions


def initial(user_config: Any, user_icons: Any, user_ignores: Any) -> Settings:
    config = merge(load_json(config_json), user_config)
    icon_c = merge(load_json(icons_json), user_icons)
    ignore = merge(load_json(ignore_json), user_ignores)

    folder_ic = icon_c["folder"]

    icons = IconSet(
        folder_open=folder_ic["open"],
        folder_closed=folder_ic["closed"],
        link=icon_c["link"],
        link_broken=icon_c["link_broken"],
        filetype=icon_c["filetype"],
        filename=icon_c["filename"],
        active=icon_c["active"],
        selected=icon_c["selected"],
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
        use_icons=config["use_icons"],
        version_ctl=version_ctl,
        width=config["width"],
    )

    return settings
