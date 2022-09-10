from dataclasses import dataclass
from pathlib import PurePath
from typing import AbstractSet, Mapping

from pynvim_pp.nvim import Marker


@dataclass(frozen=True)
class Markers:
    quick_fix: Mapping[PurePath, int]
    bookmarks: Mapping[PurePath, AbstractSet[Marker]]
