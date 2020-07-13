from typing import Any

from .consts import config_json, icons_json, ignore_json
from .da import load_json
from .types import IconSet, Keymap, Settings, UpdateTime


def initial(user_settings: Any, user_icons: Any) -> Settings:
    config = load_json(config_json)
    icon_c = load_json(icons_json)
    ignore = load_json(ignore_json)
    keymap = Keymap(entire=config["keys"], buffer=config["keymap"])

    folder_ic = icon_c["folder"]

    icons = IconSet(
        folder_open=folder_ic["open"],
        folder_closed=folder_ic["closed"],
        link=icon_c["link"],
        filetype=icon_c["filetype"],
        filename=icon_c["filename"],
    )

    update = UpdateTime(
        min_time=config["update_time"]["min"], max_time=config["update_time"]["max"]
    )

    settings = Settings(
        width=config["width"],
        open_left=config["open_left"],
        keymap=keymap,
        show_hidden=config["show_hidden"],
        follow=config["follow"],
        name_ignore=ignore["name"],
        path_ignore=ignore["path"],
        use_icons=config["use_icons"],
        icons=icons,
        update=update,
        session=config["session"],
    )

    return settings
