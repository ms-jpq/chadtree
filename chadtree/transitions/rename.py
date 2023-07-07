from os.path import abspath, normpath
from pathlib import PurePath
from typing import Optional

from pynvim_pp.hold import hold_win
from pynvim_pp.nvim import Nvim
from pynvim_pp.window import Window
from std2 import anext

from ..fs.ops import ancestors, exists, rename
from ..lsp.notify import lsp_moved
from ..registry import rpc
from ..settings.localization import LANG
from ..state.next import forward
from ..state.types import State
from .shared.current import maybe_path_above
from .shared.index import indices
from .shared.refresh import refresh
from .shared.wm import kill_buffers
from .types import Stage


@rpc(blocking=False)
async def _rename(state: State, is_visual: bool) -> Optional[Stage]:
    """
    rename file / folder
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        old_path = node.path
        child = await Nvim.input(question=LANG("pencil"), default=old_path.name)
        if not child:
            return None
        else:
            new_path = PurePath(abspath(old_path.parent / child))
            operations = {old_path: new_path}
            if await exists(new_path, follow=False):
                await Nvim.write(
                    LANG("already_exists", name=normpath(new_path)), error=True
                )
                return None
            else:
                killed = await kill_buffers(
                    last_used=state.window_order,
                    paths={old_path},
                    reopen={old_path: new_path},
                )
                try:
                    await rename(operations)
                except Exception as e:
                    await Nvim.write(e, error=True)
                    return await refresh(state=state)
                else:
                    async with hold_win(win=None):
                        for win, new_path in killed.items():
                            await Window.set_current(win)
                            escaped = await Nvim.fn.fnameescape(str, normpath(new_path))
                            await Nvim.exec(f"edit! {escaped}")

                    new_state = await maybe_path_above(state, paths={new_path}) or state
                    parents = ancestors(new_path)
                    invalidate_dirs = (parents - state.index) | {
                        old_path.parent,
                        new_path.parent,
                    }
                    index = state.index | parents
                    new_selection = {new_path} if state.selection else frozenset()
                    next_state = await forward(
                        new_state,
                        index=index,
                        invalidate_dirs=invalidate_dirs,
                        selection=new_selection,
                    )
                    await lsp_moved(operations)
                    return Stage(next_state, focus=new_path)
