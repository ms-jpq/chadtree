from pathlib import Path, PurePath
from typing import Mapping, cast

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType

from ..state.types import Diagnostics

_LUA = (Path(__file__).resolve(strict=True).parent / "diagnostics.lua").read_text(
    "UTF-8"
)


async def poll() -> Diagnostics:
    diagnostics: Mapping[str, Mapping[str, int]] = cast(
        Mapping[str, Mapping[str, int]], await Nvim.fn.luaeval(NoneType, _LUA, ())
    )

    return {
        PurePath(path): {
            int(severity): count for severity, count in (counts or {}).items()
        }
        for path, counts in (diagnostics or {}).items()
    }
