from pathlib import Path, PurePath
from typing import Any, Iterable, Mapping

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType

_LUA = (Path(__file__).resolve(strict=True).parent / "notify.lua").read_text("UTF-8")


async def _notify(method: str, params: Any) -> None:
    await Nvim.fn.luaeval(NoneType, _LUA, (method, params))


async def lsp_created(paths: Iterable[PurePath]) -> None:
    params = {"files": tuple({"uri": path.as_uri()} for path in paths)}
    await _notify("workspace/didCreateFiles", params=params)


async def lsp_removed(paths: Iterable[PurePath]) -> None:
    params = {"files": tuple({"uri": path.as_uri()} for path in paths)}
    await _notify("workspace/didDeleteFiles", params=params)


async def lsp_moved(paths: Mapping[PurePath, PurePath]) -> None:
    params = {
        "files": tuple(
            {"oldUri": old.as_uri(), "newUri": new.as_uri()}
            for old, new in paths.items()
        )
    }
    await _notify("workspace/didRenameFiles", params=params)
