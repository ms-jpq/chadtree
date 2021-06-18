from dataclasses import dataclass, field
from pathlib import PurePath
from typing import AbstractSet, Mapping


@dataclass(frozen=True)
class VCStatus:
    ignored: AbstractSet[PurePath] = frozenset()
    status: Mapping[PurePath, str] = field(default_factory=dict)

