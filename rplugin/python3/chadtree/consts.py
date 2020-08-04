from os import environ
from os.path import dirname, join, realpath
from pathlib import Path

__base__ = dirname(dirname(dirname(dirname(realpath(__file__)))))
__config__ = join(__base__, "config")
__artifacts__ = join(__base__, "artifacts")

session_dir = join(
    environ.get("XDG_DATA_HOME", join(Path.home(), ".local", "share")),
    "nvim",
    "chadtree",
)

settings_var = "chadtree_settings"
view_var = "chadtree_view"
ignores_var = "chadtree_ignores"

config_json = join(__config__, "config.json")
view_json = join(__config__, "view.json")
ignore_json = join(__config__, "ignore.json")

icons_json = join(__artifacts__, "base_icons.json")
colours_json = join(__artifacts__, "github_colours.json")

fm_filetype = "chadtree"
fm_namespace = "chadtree_ns"
fm_hl_prefix = "chadtree"

folder_mode = 0o755
file_mode = 0o644

throttle_duration = 1
