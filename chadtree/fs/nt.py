import sys
from pathlib import PurePath

if sys.version_info >= (3, 12) and sys.platform == "win32":

    from os.path import isjunction

    is_junction = isjunction
else:

    def is_junction(path: PurePath) -> bool:
        return False
