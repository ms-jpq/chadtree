from dataclasses import dataclass
from pathlib import PurePath
from typing import AbstractSet, Mapping


@dataclass(frozen=True)
class Markers:
    quick_fix: Mapping[PurePath, int]
    bookmarks: AbstractSet[PurePath]
