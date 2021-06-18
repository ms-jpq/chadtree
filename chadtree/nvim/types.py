from dataclasses import dataclass
from pathlib import PurePath
from typing import Mapping


@dataclass(frozen=True)
class QuickFix:
    locations: Mapping[PurePath, int]

