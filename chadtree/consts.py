from os import environ
from pathlib import Path

_TOP_LEVEL = Path(__file__).parent.parent
_CONFIG = _TOP_LEVEL / "config"
_ARTIFACTS = _TOP_LEVEL / "artifacts"

session_dir = (
    Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    / "nvim"
    / "chadtree"
)

settings_var = "chadtree_settings"
view_var = "chadtree_view"
colours_var = "chadtree_colours"
ignores_var = "chadtree_ignores"

config_json = _CONFIG / "config.json"
view_json = _CONFIG / "view.json"
ignore_json = _CONFIG / "ignore.json"

lang_root = _TOP_LEVEL / "locale"
default_lang = "en"

unicode_icons_json = _ARTIFACTS / "unicode_icons.json"
ascii_icons_json = _ARTIFACTS / "ascii_icons.json"
emoji_icons_json = _ARTIFACTS / "emoji_icons.json"
icon_lookup = {
    True: unicode_icons_json,
    False: ascii_icons_json,
    "emoji": emoji_icons_json,
}

colours_json = _ARTIFACTS / "github_colours.json"
custom_colours_json = _CONFIG / "colours.json"

fm_filetype = "CHADTree"
fm_namespace = "chadtree_ns"
fm_hl_prefix = "chadtree"

folder_mode = 0o755
file_mode = 0o644

throttle_duration = 1
