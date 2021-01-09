from dataclasses import dataclass
from typing import Optional

from ..state.types import State


@dataclass(frozen=True)
class Stage:
    state: State
    focus: Optional[str] = None


class SysError(Exception):
    ...
