from pathlib import PurePath
from typing import MutableMapping, Optional

from pynvim_pp.nvim import Nvim

from ..fs.ops import exists, link
from ..lsp.notify import lsp_created
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.current import maybe_path_above
from .shared.index import indices
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
async def _link(state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    Symlink selected
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if node is None:
        return None
    else:
        selection = state.selection or {node.path}
        operations: MutableMapping[PurePath, PurePath] = {}
        for src in selection:
            if child := await Nvim.input(question=LANG("link"), default=""):
                dst = node.path.parent / child
                if dst in operations or await exists(dst, follow=False):
                    await Nvim.write(LANG("already_exists", name=str(dst)), error=True)
                    return None
                else:
                    operations[dst] = src
            else:
                return None

        try:
            await link(operations)
        except Exception as e:
            await Nvim.write(e, error=True)
            return await refresh(state=state, settings=settings)
        else:
            new_state = (
                await maybe_path_above(state, settings=settings, path=path) or state
            )
            paths = ancestors(path)
            index = state.index | paths
            next_state = await forward(
                new_state, settings=settings, index=index, paths=paths
            )
            await lsp_created((path,))
            return Stage(next_state, focus=path)
