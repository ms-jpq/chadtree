from dataclasses import dataclass, field
from pathlib import PurePath
from typing import AbstractSet, Mapping, MutableMapping


@dataclass(frozen=True)
class VCStatus:
    main: str = ""
    submodules: str = ""
    ignored: AbstractSet[PurePath] = frozenset()
    status: Mapping[PurePath, str] = field(default_factory=dict)
    ignore_cache: MutableMapping[PurePath, bool] = field(default_factory=dict)
