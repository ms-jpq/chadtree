from os import sep
from os.path import abspath, dirname, join
from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import ask
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, exists, new
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
        parent = node.path if is_dir(node) else dirname(node.path)

        child = ask(nvim, question=LANG("pencil"), default="")

        if not child:
            return None
        else:
            path = abspath(join(parent, child))
            if exists(path, follow=False):
                write(nvim, LANG("already_exists", name=path), error=True)
                return None
            else:
                try:
                    dest = path + sep if child.endswith(sep) else path
                    new((dest,))
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
                    return Stage(next_state, focus=path)
