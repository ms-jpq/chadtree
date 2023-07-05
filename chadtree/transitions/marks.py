from locale import strxfrm
from pathlib import PurePath
from typing import Any, Iterator, MutableMapping, MutableSet, Optional, Tuple

from pynvim_pp.nvim import Nvim
from std2.locale import pathsort_key
from std2.pathlib import is_relative_to

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from ..view.ops import display_path
from .focus import _jump
from .types import Stage


def _order(root: PurePath, marks: str, path: PurePath) -> Tuple[bool, str, Any]:
    return not is_relative_to(path, root), "", pathsort_key(path)


def _display_path(state: State, marks: str, path: PurePath, idx: int) -> str:
    display = display_path(path, state=state)
    return f"{idx}. [{marks}] {display}"


@rpc(blocking=False)
async def _bookmark_goto(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Goto bookmark
    """

    def cont() -> Iterator[Tuple[str, PurePath]]:
        root = state.root.path
        markers: MutableMapping[str, PurePath] = {}
        for path, marks in state.markers.bookmarks.items():
            for mark in marks:
                if m := markers.get(mark):
                    markers[mark] = max(m, path)
                else:
                    markers[mark] = path

        seen: MutableSet[PurePath] = set()
        for _, path in sorted(markers.items(), key=lambda kv: _order(root, *kv)):
            if path not in seen:
                ms = sorted(state.markers.bookmarks.get(path, ()), key=strxfrm)
                yield "".join(ms), path

    opts = {
        _display_path(state, marks=marks, path=path, idx=idx): path
        for idx, (marks, path) in enumerate(cont(), start=1)
    }

    if mark := await Nvim.input_list(opts):
        return await _jump(state, settings=settings, path=mark)
    else:
        await Nvim.write(LANG("no_bookmarks"), error=True)
        return None
