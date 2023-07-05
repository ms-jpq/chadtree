from locale import strxfrm
from pathlib import PurePath
from typing import Iterator, MutableMapping, MutableSet, Optional, Tuple

from pynvim_pp.nvim import Nvim

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..view.ops import display_path
from .focus import _jump
from .types import Stage


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
        markers: MutableMapping[str, PurePath] = {}
        for path, marks in state.markers.bookmarks.items():
            for mark in marks:
                markers[mark] = path

        seen: MutableSet[PurePath] = set()
        for _, path in sorted(markers.items()):
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
