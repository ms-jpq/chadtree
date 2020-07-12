from typing import Any

from .consts import config_json, icons_json
from .da import load_json
from .types import VCIcons, IconSet, Keymap, Settings


def initial(user_settings: Any, user_icons: Any) -> Settings:
    config = load_json(config_json)
    icon_c = load_json(icons_json)
    keymap = Keymap(entire=config["keys"], buffer=config["keymap"])

    vc_ic = icon_c["vc"]
    vc_icons = VCIcons(
        ignored=vc_ic["ignored"],
        untracked=vc_ic["untracked"],
        modified=vc_ic["modified"],
        staged=vc_ic["staged"],
    )

    icons = IconSet(
        folder=icon_c["folder"],
        link=icon_c["link"],
        vc=vc_icons,
        filetype=icon_c["filetype"],
    )

    settings = Settings(
        width=config["width"],
        open_left=config["open_left"],
        keymap=keymap,
        show_hidden=config["show_hidden"],
        name_ignore=config["name_ignore"],
        path_ignore=config["path_ignore"],
        use_icons=config["use_icons"],
        icons=icons,
    )

    return settings
