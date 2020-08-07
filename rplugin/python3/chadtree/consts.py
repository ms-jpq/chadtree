from os import environ
from os.path import dirname, join, realpath
from pathlib import Path

__base__ = dirname(dirname(dirname(dirname(realpath(__file__)))))
__config__ = join(__base__, "config")
__artifacts__ = join(__base__, "artifacts")
__log_file__ = join(__base__, "logs", "chad.log")

session_dir = join(
    environ.get("XDG_DATA_HOME", join(Path.home(), ".local", "share")),
    "nvim",
    "chadtree",
)

settings_var = "chadtree_settings"
view_var = "chadtree_view"
colours_var = "chadtree_colours"
ignores_var = "chadtree_ignores"

config_json = join(__config__, "config.json")
view_json = join(__config__, "view.json")
ignore_json = join(__config__, "ignore.json")

unicode_icons_json = join(__artifacts__, "unicode_icons.json")
ascii_icons_json = join(__artifacts__, "ascii_icons.json")
emoji_icons_json = join(__artifacts__, "emoji_icons.json")
icon_lookup = {
    True: unicode_icons_json,
    False: ascii_icons_json,
    "emoji": emoji_icons_json,
}

colours_json = join(__artifacts__, "github_colours.json")
custom_colours_json = join(__config__, "colours.json")

fm_filetype = "CHADTree"
fm_namespace = "chadtree_ns"
fm_hl_prefix = "chadtree"

folder_mode = 0o755
file_mode = 0o644

throttle_duration = 1
