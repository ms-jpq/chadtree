from os import sep
from os.path import abspath, normpath
from pathlib import PurePath
from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, exists, mkdir, new
from ..lsp.notify import lsp_created
from ..registry import rpc
from ..settings.localization import LANG
from ..state.next import forward
from ..state.types import State
from .shared.current import maybe_path_above
from .shared.index import indices
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
async def _new(state: State, is_visual: bool) -> Optional[Stage]:
    """
    new file / folder
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        parent = node.path if is_dir(node) else node.path.parent

        child = await Nvim.input(question=LANG("pencil"), default="")

        if not child:
            return None
        else:
            path = PurePath(abspath(parent / child))
            if await exists(path, follow=False):
                await Nvim.write(
                    LANG("already_exists", name=normpath(path)), error=True
                )
                return None
            else:
                try:
                    if child.endswith(sep):
                        await mkdir((path,))
                    else:
                        await new((path,))
                except Exception as e:
                    await Nvim.write(e, error=True)
                    return await refresh(state=state)
                else:
                    new_state = await maybe_path_above(state, paths={path}) or state
                    parents = ancestors(path)
                    invalidate_dirs = (parents - state.index) | {path.parent}
                    index = state.index | parents
                    new_selection = {path} if state.selection else frozenset()
                    next_state = await forward(
                        new_state,
                        index=index,
                        invalidate_dirs=invalidate_dirs,
                        selection=new_selection,
                    )
                    await lsp_created((path,))
                    return Stage(next_state, focus=path)
