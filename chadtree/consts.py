from os import name
from stat import S_IRGRP, S_IROTH, S_IRUSR, S_IWUSR, S_IXGRP, S_IXUSR, S_IXOTH

from chad_types import TOP_LEVEL

GIL_SWITCH = 1 / 1000
IS_WIN = name == "nt"
REQUIREMENTS = TOP_LEVEL / "requirements.txt"

FOLDER_MODE = (S_IRUSR | S_IWUSR | S_IXUSR) | (S_IRGRP | S_IXGRP) | (S_IROTH | S_IXOTH)
FILE_MODE = (S_IRUSR | S_IWUSR) | (S_IRGRP) | (S_IROTH)

WALK_PARALLELISM_FACTOR = 100
RENDER_RETRIES = 3

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
RT_PY = RT_DIR / "Scripts" / "python.exe" if IS_WIN else RT_DIR / "bin" / "python3"
SESSION_DIR = _VARS / "sessions"


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
