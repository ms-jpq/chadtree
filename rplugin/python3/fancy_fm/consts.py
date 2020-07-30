from os import environ
from os.path import dirname, join, realpath
from pathlib import Path

__base__ = dirname(dirname(dirname(dirname(realpath(__file__)))))
__config__ = join(__base__, "config")
__artifacts__ = join(__base__, "artifacts")

session_dir = join(
    environ.get("XDG_DATA_HOME", join(Path.home(), ".local", "share")),
    "nvim",
    "fancy_fm",
)

config_json = join(__config__, "config.json")
view_json = join(__config__, "view.json")
icons_json = join(__config__, "icons.json")
colours_json = join(__artifacts__, "github_colours.json")
ignore_json = join(__config__, "ignore.json")

fm_filetype = "fancy_fm"
fm_namespace = "fancy_fm_ns"
fm_hl_prefix = "fancy_fm_"

folder_mode = 0o755
file_mode = 0o644

throttle_duration = 1
