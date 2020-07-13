from os import environ
from os.path import dirname, join
from pathlib import Path

__base__ = dirname(dirname(dirname(dirname(__file__))))
__config__ = join(__base__, "config")

session_dir = join(
    environ.get("XDG_DATA_HOME", join(Path.home(), ".local", "share")),
    "nvim",
    "fast_fm",
)

config_json = join(__config__, "config.json")
icons_json = join(__config__, "icons.json")
ignore_json = join(__config__, "ignore.json")

fm_filetype = "fast_fm"

folder_mode = 0o755
file_mode = 0o644
