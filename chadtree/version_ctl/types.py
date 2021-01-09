from dataclasses import dataclass, field
from typing import FrozenSet, Mapping


@dataclass(frozen=True)
class VCStatus:
    ignored: FrozenSet[str] = frozenset()
    status: Mapping[str, str] = field(default_factory=dict)
