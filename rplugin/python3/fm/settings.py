from .consts import config_json
from .da import load_json
from .types import Settings


def initial() -> Settings:
    config = load_json(config_json)
    ignored = set(config["ignored"])
    keymap = config["keymap"]
    icons = config["icons"]
    settings = Settings(width=40, keymap=keymap, ignored=ignored, icons=icons)
    return settings
