from os import environ
from pathlib import Path

FOLDER_MODE = 0o755
FILE_MODE = 0o644


_TOP_LEVEL = Path(__file__).parent.parent
_CONFIG = _TOP_LEVEL / "config"
_ARTIFACTS = _TOP_LEVEL / "artifacts"


RT_DIR = _TOP_LEVEL / ".vars" / "runtime"
REQUIREMENTS = str(_TOP_LEVEL / "requirements.txt")


SESSION_DIR = (
    Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    / "nvim"
    / "chadtree"
)


SETTINGS_VAR = "chadtree_settings"
VIEW_VAR = "chadtree_view"
COLOURS_VAR = "chadtree_colours"
IGNORES_VAR = "chadtree_ignores"


CONFIG_YML = _CONFIG / "config.yml"
VIEW_YML = _CONFIG / "view.yml"
IGNORE_YML = _CONFIG / "ignore.yml"


LANG_ROOT = _TOP_LEVEL / "locale"
DEFAULT_LANG = "en"


_UNICODE_ICONS_JSON = _ARTIFACTS / "unicode_icons.json"
_ASCII_ICONS_JSON = _ARTIFACTS / "ascii_icons.json"
_EMOJI_ICONS_JSON = _ARTIFACTS / "emoji_icons.json"
ICON_LOOKUP_JSON = {
    True: _UNICODE_ICONS_JSON,
    False: _ASCII_ICONS_JSON,
    "emoji": _EMOJI_ICONS_JSON,
}


COLOURS_JSON = _ARTIFACTS / "github_colours.json"
CUSTOM_COLOURS_YML = _CONFIG / "colours.yml"


FM_FILETYPE = "CHADTree"
FM_NAMESPACE = "chadtree_ns"
FM_HL_PREFIX = "chadtree"


MIGRATION_URI = "https://github.com/ms-jpq/chadtree/blob/chad/docs/MIGRATION.md"

_DOCS_DIR = _TOP_LEVEL / "docs"
README_MD = _DOCS_DIR / "README.md"
FEATURES_MD = _DOCS_DIR / "FEATURES.md"
KEYBIND_MD = _DOCS_DIR / "KEYBIND.md"
CONFIGURATION_MD = _DOCS_DIR / "CONFIGURATION.md"
THEME_MD = _DOCS_DIR / "THEME.md"