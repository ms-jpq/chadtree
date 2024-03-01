import sys
from collections import Counter
from pathlib import Path, PurePath
from typing import Mapping, MutableMapping, cast

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType

from ..fs.ops import ancestors
from ..state.types import Diagnostics

_LUA = (
    Path(__file__).resolve(strict=True).with_name("diagnostics.lua").read_text("UTF-8")
)

if sys.version_info < (3, 9):
    _C = Counter
else:
    _C = Counter[int]


async def poll(min_severity: int) -> Diagnostics:
    diagnostics: Mapping[str, Mapping[str, int]] = cast(
        Mapping[str, Mapping[str, int]], await Nvim.fn.luaeval(NoneType, _LUA, ())
    )

    raw = {
        PurePath(path): Counter(
            {
                s: count
                for severity, count in (counts or {}).items()
                if (s := int(severity)) <= min_severity
            }
        )
        for path, counts in (diagnostics or {}).items()
    }

    acc: MutableMapping[PurePath, _C] = {}
    for path, counts in raw.items():
        for parent in ancestors(path):
            c = acc.setdefault(parent, Counter())
            c += counts

    return {**acc, **raw}
