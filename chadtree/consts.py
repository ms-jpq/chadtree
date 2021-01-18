from os import environ
from pathlib import Path

WALK_PARALLELISM_FACTOR = 100
FOLDER_MODE = 0o755
FILE_MODE = 0o644
WARN_DURATION = 0.1

_TOP_LEVEL = Path(__file__).parent.parent
_CONFIG = _TOP_LEVEL / "config"
_ARTIFACTS = _TOP_LEVEL / "artifacts"


RT_DIR = _TOP_LEVEL / ".vars" / "runtime"
REQUIREMENTS = str(_TOP_LEVEL / "requirements.txt")


FM_FILETYPE = "CHADTree"
FM_NAMESPACE = "chadtree_ns"
FM_HL_PREFIX = "chadtree"


SETTINGS_VAR = "chadtree_settings"


CONFIG_YML = _CONFIG / "config.yml"


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


GITHUB_COLOURS_JSON = _ARTIFACTS / "github_colours.json"
NERD_COLOURS_JSON = _ARTIFACTS / "colours_night.json"


SESSION_DIR = (
    Path(environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    / "nvim"
    / "chadtree"
)


_DOCS_URI_BASE = "https://github.com/ms-jpq/chadtree/blob/future2/docs"
_DOCS_DIR = _TOP_LEVEL / "docs"

MIGRATION_URI = f"{_DOCS_URI_BASE}/MIGRATION.md"

_README_md = "README.md"
README_MD = _DOCS_DIR / _README_md
README_URI = f"{_DOCS_URI_BASE}/{_README_md}"

_FEATURES_md = "FEATURES.md"
FEATURES_MD = _DOCS_DIR / _FEATURES_md
FEATURES_URI = f"{_DOCS_URI_BASE}/{_FEATURES_md}"

_KEYBIND_md = "KEYBIND.md"
KEYBIND_MD = _DOCS_DIR / _KEYBIND_md
KEYBIND_URI = f"{_DOCS_URI_BASE}/{_KEYBIND_md}"

_CONFIGURATION_md = "CONFIGURATION.md"
CONFIGURATION_MD = _DOCS_DIR / _CONFIGURATION_md
CONFIGURATION_URI = f"{_DOCS_URI_BASE}/{_CONFIGURATION_md}"

_THEME_md = "THEME.md"
THEME_MD = _DOCS_DIR / _THEME_md
THEME_URI = f"{_DOCS_URI_BASE}/{_THEME_md}"
