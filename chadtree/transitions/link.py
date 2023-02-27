from os.path import normpath, relpath
from pathlib import Path, PurePath
from typing import MutableMapping, Optional

from pynvim_pp.nvim import Nvim
from std2.locale import pathsort_key

from ..fs.ops import ancestors, exists, link
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
        selection = state.selection or {node.path}
        operations: MutableMapping[PurePath, PurePath] = {}
        for selected in selection:
            display = display_path(selected, state=state)
            if child := await Nvim.input(
                question=LANG("link", src=display), default=""
            ):
                try:
                    dst = Path(node.path.parent / child).resolve()
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
            ancestry = ancestors(*paths)
            index = state.index | ancestry
            next_state = await forward(
                new_state, settings=settings, index=index, paths=ancestry
            )
            return Stage(next_state, focus=focus)
