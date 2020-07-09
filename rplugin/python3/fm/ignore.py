from fnmatch import fnmatch
from typing import Callable, Sequence, Set


def ignore(matches: Sequence[str], git: Set[str]) -> Callable[[str], bool]:
    def ignore(path: str) -> bool:
        return path in git or any(fnmatch(path, match) for match in matches)

    return ignore
