from os import chmod, stat, stat_result
from pathlib import PurePath
from stat import S_ISDIR, S_IXGRP, S_IXOTH, S_IXUSR
from typing import Iterator, Tuple

from ..fs.cartographer import is_dir
from ..registry import rpc
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _toggle_exec(state: State, is_visual: bool) -> Stage:
    """
    Toggle chmod +-x
    """

    selected = state.selection or {
        node.path
        async for node in indices(state, is_visual=is_visual)
        if not is_dir(node)
    }

    def cont() -> Iterator[Tuple[PurePath, stat_result]]:
        for path in selected:
            try:
                st = stat(path)
            except FileNotFoundError:
                pass
            else:
                if not S_ISDIR(st.st_mode):
                    yield path, st

    stats = {path: st for path, st in cont()}

    for path, st in stats.items():
        chmod(path, st.st_mode ^ S_IXUSR ^ S_IXGRP ^ S_IXOTH)

    invalidate_dirs = {path.parent for path in stats.keys()}
    new_state = await forward(state, invalidate_dirs=invalidate_dirs)
    return Stage(state=new_state)
