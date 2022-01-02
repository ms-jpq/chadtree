from pathlib import Path, PurePath
from typing import Any, Iterable, Mapping

from pynvim import Nvim

_LUA = (Path(__file__).resolve(strict=True).parent / "notify.lua").read_text("UTF-8")


def _notify(nvim: Nvim, method: str, params: Any) -> None:
    nvim.funcs.luaeval(_LUA, (method, params))


def lsp_created(nvim: Nvim, paths: Iterable[PurePath]) -> None:
    params = {"files": tuple({"uri": path.as_uri()} for path in paths)}
    _notify(nvim, method="workspace/didCreateFiles", params=params)


def lsp_removed(nvim: Nvim, paths: Iterable[PurePath]) -> None:
    params = {"files": tuple({"uri": path.as_uri()} for path in paths)}
    _notify(nvim, method="workspace/didDeleteFiles", params=params)


def lsp_moved(nvim: Nvim, paths: Mapping[PurePath, PurePath]) -> None:
    params = {
        "files": tuple(
            {"oldUri": old.as_uri(), "newUri": new.as_uri()}
            for old, new in paths.items()
        )
    }
    _notify(nvim, method="workspace/didRenameFiles", params=params)
