from os.path import abspath
from pathlib import PurePath
from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import ask
from pynvim_pp.lib import write

from ..fs.ops import ancestors, exists, rename
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.current import maybe_path_above
from .shared.index import indices
from .shared.refresh import refresh
from .shared.wm import kill_buffers
from .types import Stage


@rpc(blocking=False)
def _rename(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    rename file / folder
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:

        child = ask(nvim, question=LANG("pencil"), default=str(node.path.name))
        if not child:
            return None
        else:
            new_path = PurePath(abspath(node.path.parent / child))

            if exists(new_path, follow=False):
                write(nvim, LANG("already_exists", name=str(new_path)), error=True)
                return None
            else:
                try:
                    rename({node.path: new_path})
                except Exception as e:
                    write(nvim, e, error=True)
                    return refresh(nvim, state=state, settings=settings)
                else:
                    new_state = (
                        maybe_path_above(
                            nvim, state=state, settings=settings, path=new_path
                        )
                        or state
                    )
                    paths = ancestors(new_path)
                    index = state.index | paths
                    next_state = forward(
                        new_state, settings=settings, index=index, paths=paths
                    )
                    kill_buffers(nvim, paths={node.path}, reopen={node.path: new_path})
                    return Stage(next_state, focus=new_path)

