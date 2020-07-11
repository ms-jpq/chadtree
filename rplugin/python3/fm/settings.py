from typing import Any

from .consts import config_json, icons_json
from .da import load_json
from .types import GitIcons, IconSet, Settings


def initial(user_settings: Any, user_icons: Any) -> Settings:
    config = load_json(config_json)
    icon_c = load_json(icons_json)

    git_ic = icon_c["git"]
    git_icons = GitIcons(
        ignored=git_ic["ignored"],
        added=git_ic["added"],
        modified=git_ic["modified"],
        staged=git_ic["staged"],
    )

    icons = IconSet(
        folder=icon_c["folder"],
        link=icon_c["link"],
        git=git_icons,
        filetype=icon_c["filetype"],
    )

    settings = Settings(
        width=config["width"],
        keymap=config["keymap"],
        show_hidden=config["show_hidden"],
        name_ignore=config["name_ignore"],
        path_ignore=config["path_ignore"],
        use_icons=config["use_icons"],
        icons=icons,
    )

    return settings
