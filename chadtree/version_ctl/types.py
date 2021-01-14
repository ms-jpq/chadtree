from dataclasses import dataclass, field
from typing import AbstractSet, Mapping


@dataclass(frozen=True)
class VCStatus:
    ignored: AbstractSet[str] = frozenset()
    status: Mapping[str, str] = field(default_factory=dict)
