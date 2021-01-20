from pathlib import Path

WALK_PARALLELISM_FACTOR = 100
FOLDER_MODE = 0o755
FILE_MODE = 0o644

_TOP_LEVEL = Path(__file__).parent.parent
_CONFIG = _TOP_LEVEL / "config"
_ARTIFACTS = _TOP_LEVEL / "artifacts"
_VARS = _TOP_LEVEL / ".vars"


RT_DIR = _VARS / "runtime"
REQUIREMENTS = str(_TOP_LEVEL / "requirements.txt")


FM_FILETYPE = "CHADTree"
FM_NAMESPACE = "chadtree_ns"
FM_HL_PREFIX = "chadtree"


SETTINGS_VAR = "chadtree_settings"


CONFIG_YML = _CONFIG / "defaults.yml"


LANG_ROOT = _TOP_LEVEL / "locale"
DEFAULT_LANG = "en"


ASCII_ICONS_JSON = _ARTIFACTS / "ascii_icons.json"
EMOJI_ICONS_JSON = _ARTIFACTS / "emoji_icons.json"
DEVI_ICONS_JSON = _ARTIFACTS / "unicode_icons.json"


GITHUB_COLOURS_JSON = _ARTIFACTS / "github_colours.json"
NERD_COLOURS_LIGHT_JSON = _ARTIFACTS / "colours_day.json"
NERD_COLOURS_DARK_JSON = _ARTIFACTS / "colours_night.json"


_DOCS_URI_BASE = "https://github.com/ms-jpq/chadtree/blob/future2/docs"
_DOCS_DIR = _TOP_LEVEL / "docs"

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


SESSION_DIR = _VARS / "sessions"