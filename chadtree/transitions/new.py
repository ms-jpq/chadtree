from os import sep
from os.path import abspath
from pathlib import PurePath
from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import ask
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, exists, mkdir, new
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
def _new(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    new file / folder
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        parent = node.path if is_dir(node) else node.path.parent

        child = ask(nvim, question=LANG("pencil"), default="")

        if not child:
            return None
        else:
            path = PurePath(abspath(parent / child))
            if exists(path, follow=False):
                write(nvim, LANG("already_exists", name=str(path)), error=True)
                return None
            else:
                try:
                    if child.endswith(sep):
                        mkdir(state.pool, paths=(path,))
                    else:
                        new(state.pool, paths=(path,))
                except Exception as e:
                    write(nvim, e, error=True)
                    return refresh(nvim, state=state, settings=settings)
                else:
                    new_state = (
                        maybe_path_above(
                            nvim, state=state, settings=settings, path=path
                        )
                        or state
                    )
                    paths = ancestors(path)
                    index = state.index | paths
                    next_state = forward(
                        new_state, settings=settings, index=index, paths=paths
                    )
                    lsp_created(nvim, paths=(path,))
                    return Stage(next_state, focus=path)
