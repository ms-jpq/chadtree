from os import environ
from pathlib import Path

_TOP_LEVEL = Path(__file__).parent.parent
_CONFIG = _TOP_LEVEL / "config"
_ARTIFACTS = _TOP_LEVEL / "artifacts"

SESSION_DIR = (
    Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    / "nvim"
    / "chadtree"
)

SETTINGS_VAR = "chadtree_settings"
VIEW_VAR = "chadtree_view"
COLOURS_VAR = "chadtree_colours"
IGNORES_VAR = "chadtree_ignores"

CONFIG_JSON = _CONFIG / "config.json"
VIEW_JSON = _CONFIG / "view.json"
IGNORE_JSON = _CONFIG / "ignore.json"

LANG_ROOT = _TOP_LEVEL / "locale"
DEFAULT_LANG = "en"

UNICODE_ICONS_JSON = _ARTIFACTS / "unicode_icons.json"
ASCII_ICONS_JSON = _ARTIFACTS / "ascii_icons.json"
EMOJI_ICONS_JSON = _ARTIFACTS / "emoji_icons.json"
ICON_LOOKUP = {
    True: UNICODE_ICONS_JSON,
    False: ASCII_ICONS_JSON,
    "emoji": EMOJI_ICONS_JSON,
}

COLOURS_JSON = _ARTIFACTS / "github_colours.json"
CUSTOM_COLOURS_JSON = _CONFIG / "colours.json"

FM_FILETYPE = "CHADTree"
FM_NAMESPACE = "chadtree_ns"
FM_HL_PREFIX = "chadtree"

FOLDER_MODE = 0o755
FILE_MODE = 0o644
