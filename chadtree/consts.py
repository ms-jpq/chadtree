from chad_types import TOP_LEVEL

WALK_PARALLELISM_FACTOR = 100
FOLDER_MODE = 0o755
FILE_MODE = 0o644


_ARTIFACTS = TOP_LEVEL / "artifacts"
_VARS = TOP_LEVEL / ".vars"


RT_DIR = _VARS / "runtime"
REQUIREMENTS = TOP_LEVEL / "requirements.txt"
DEPS_LOCK = _VARS / "deps.lock"


FM_FILETYPE = "CHADTree"
FM_NAMESPACE = "chadtree_ns"
FM_HL_PREFIX = "chadtree"


DEFAULT_LANG = "en"
LANG_ROOT = TOP_LEVEL / "locale"
CONFIG_YML = TOP_LEVEL / "config" / "defaults.yml"
SETTINGS_VAR = "chadtree_settings"


ASCII_ICONS_JSON = _ARTIFACTS / "ascii_icons.json"
EMOJI_ICONS_JSON = _ARTIFACTS / "emoji_icons.json"
DEVI_ICONS_JSON = _ARTIFACTS / "unicode_icons.json"


GITHUB_COLOURS_JSON = _ARTIFACTS / "github_colours.json"
NERD_COLOURS_LIGHT_JSON = _ARTIFACTS / "colours_day.json"
NERD_COLOURS_DARK_JSON = _ARTIFACTS / "colours_night.json"


"""
Docs
"""


_DOCS_URI_BASE = "https://github.com/ms-jpq/chadtree/blob/future2/docs"
_DOCS_DIR = TOP_LEVEL / "docs"

MIGRATION_URI = f"{_DOCS_URI_BASE}/MIGRATION.md"

_README_md = "README.md"
README_MD = _DOCS_DIR / _README_md
README_URI = f"{_DOCS_URI_BASE}"

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


"""
Sessions
"""


SESSION_DIR = _VARS / "sessions"
