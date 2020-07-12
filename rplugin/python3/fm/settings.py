from typing import Any

from .consts import config_json, icons_json, ignore_json
from .da import load_json
from .types import IconSet, Keymap, Settings, VCIcons


def initial(user_settings: Any, user_icons: Any) -> Settings:
    config = load_json(config_json)
    icon_c = load_json(icons_json)
    ignore = load_json(ignore_json)
    keymap = Keymap(entire=config["keys"], buffer=config["keymap"])

    vc_ic = icon_c["vc"]
    vc_icons = VCIcons(
        ignored=vc_ic["ignored"],
        untracked=vc_ic["untracked"],
        modified=vc_ic["modified"],
        staged=vc_ic["staged"],
    )

    folder_ic = icon_c["folder"]

    icons = IconSet(
        folder_open=folder_ic["open"],
        folder_closed=folder_ic["closed"],
        link=icon_c["link"],
        vc=vc_icons,
        filetype=icon_c["filetype"],
        filename=icon_c["filename"],
    )

    settings = Settings(
        width=config["width"],
        open_left=config["open_left"],
        keymap=keymap,
        show_hidden=config["show_hidden"],
        name_ignore=ignore["name"],
        path_ignore=ignore["path"],
        use_icons=config["use_icons"],
        icons=icons,
    )

    return settings
