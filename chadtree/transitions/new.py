from os.path import abspath, dirname, exists, join
from typing import Optional

from pynvim import Nvim
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, new
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .shared.open_file import open_file
from .shared.refresh import refresh
from .types import ClickType, Stage


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

        child: Optional[str] = nvim.funcs.input(LANG("pencil"))

        if not child:
            return None
        else:
            path = abspath(join(parent, child))
            if exists(path):
                write(nvim, LANG("already_exists", name=path), error=True)
                return None
            else:
                try:
                    new((path,))
                except Exception as e:
                    write(nvim, e, error=True)
                    return refresh(nvim, state=state, settings=settings)
                else:
                    paths = ancestors(path)
                    index = state.index | paths
                    new_state = forward(
                        state, settings=settings, index=index, paths=paths
                    )
                    nxt = open_file(
                        nvim,
                        state=new_state,
                        settings=settings,
                        path=path,
                        click_type=ClickType.secondary,
                    )
                    return nxt
