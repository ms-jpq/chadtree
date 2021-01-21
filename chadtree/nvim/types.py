from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class QuickFix:
    locations: Mapping[str, int]
