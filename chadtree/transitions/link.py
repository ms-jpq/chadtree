from os.path import normpath, relpath
from pathlib import PurePath
from typing import MutableMapping, Optional

from pynvim_pp.nvim import Nvim
from std2 import anext
from std2.locale import pathsort_key

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, exists, link, resolve
from ..lsp.notify import lsp_created
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..view.ops import display_path
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
        parent = node.path if is_dir(node) else node.path.parent
        selection = state.selection or {node.path}
        operations: MutableMapping[PurePath, PurePath] = {}
        for selected in selection:
            display = display_path(selected, state=state)
            if child := await Nvim.input(
                question=LANG("link", src=display), default=""
            ):
                try:
                    dst = await resolve(parent / child, strict=False)
                except Exception as e:
                    await Nvim.write(e, error=True)
                    return None
                else:
                    if dst in operations or await exists(dst, follow=False):
                        await Nvim.write(
                            LANG("already_exists", name=normpath(dst)), error=True
                        )
                        return None
                    else:
                        src = PurePath(relpath(selected, start=dst.parent))
                        operations[dst] = src
            else:
                return None

        try:
            await link(operations)
        except Exception as e:
            await Nvim.write(e, error=True)
            return await refresh(state=state, settings=settings)
        else:
            paths = operations.keys()
            new_state = (
                await maybe_path_above(state, settings=settings, paths=paths) or state
            )
            await lsp_created(paths)
            focus, *_ = sorted(paths, key=pathsort_key)
            parents = ancestors(*paths)
            invalidate_dirs = (parents - state.index) | {path.parent for path in paths}
            index = state.index | parents
            new_selection = paths if state.selection else frozenset()
            next_state = await forward(
                new_state,
                settings=settings,
                index=index,
                invalidate_dirs=invalidate_dirs,
                selection=new_selection,
            )
            return Stage(next_state, focus=focus)
