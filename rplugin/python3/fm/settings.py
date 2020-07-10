from .consts import config_json
from .da import load_json
from .types import Settings


def initial() -> Settings:
    config = load_json(config_json)
    settings = Settings(
        width=config["width"],
        keymap=config["keymap"],
        name_ignore=config["name_ignore"],
        path_ignore=config["path_ignore"],
    )
    return settings
