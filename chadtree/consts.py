from os import environ
from pathlib import Path

from chad_types import TOP_LEVEL

WALK_PARALLELISM_FACTOR = 100
FOLDER_MODE = 0o755
FILE_MODE = 0o644

REQUIREMENTS = TOP_LEVEL / "requirements.txt"

FM_FILETYPE = "CHADTree"
FM_NAMESPACE = "chadtree_ns"
FM_HL_PREFIX = "chadtree"

DEFAULT_LANG = "en"
LANG_ROOT = TOP_LEVEL / "locale"
CONFIG_YML = TOP_LEVEL / "config" / "defaults.yml"
SETTINGS_VAR = "chadtree_settings"

"""
STORAGE
"""

_VARS = TOP_LEVEL / ".vars"
RT_DIR = _VARS / "runtime"
RT_PY = str(RT_DIR / "bin" / "python3")
SESSION_DIR = _VARS / "sessions"

_XDG_DATA_DIR = Path(environ.get("XDG_DATA_HOME", _VARS))
_XDG_VARS = _XDG_DATA_DIR / "nvim" / "chadtree"
RT_DIR_XDG = _XDG_VARS / "runtime"
RT_PY_XDG = str(RT_DIR_XDG / "bin" / "python3")
SESSION_DIR_XDG = _XDG_VARS / "sessions"

"""
Docs
"""


_DOCS_URI_BASE = "https://github.com/ms-jpq/chadtree/blob/chad/docs"
_DOCS_DIR = TOP_LEVEL / "docs"


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

_MIGRATION_md = "MIGRATION.md"
MIGRATION_MD = _DOCS_DIR / _MIGRATION_md
MIGRATION_URI = f"{_DOCS_URI_BASE}/{_MIGRATION_md}"
