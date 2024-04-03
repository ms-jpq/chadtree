import sys
from os import stat_result
from stat import S_ISDIR

if sys.platform == "win32":

    def is_junction(st: stat_result) -> bool:
        return bool(S_ISDIR(st.st_mode) and st.st_reparse_tag)

else:

    def is_junction(st: stat_result) -> bool:
        return False
