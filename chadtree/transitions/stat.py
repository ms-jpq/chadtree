from pynvim_pp.nvim import Nvim
from std2 import anext
from std2.locale import si_prefixed

from ..fs.ops import fs_stat
from ..registry import rpc
from ..state.types import State
from ..view.ops import display_path
from .shared.index import indices


@rpc(blocking=False)
async def _stat(state: State, is_visual: bool) -> None:
    """
    Print file stat to cmdline
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        try:
            stat = await fs_stat(node.path)
        except Exception as e:
            await Nvim.write(e, error=True)
        else:
            permissions = stat.permissions
            size = si_prefixed(stat.size, precision=2)
            user = stat.user
            group = stat.group
            mtime = stat.date_mod.strftime(state.settings.view.time_fmt)
            name = display_path(node.path, state=state)
            full_name = f"{name} -> {stat.link}" if stat.link else name
            mode_line = f"{permissions} {size}b {user} {group} {mtime} {full_name}"
            await Nvim.write(mode_line)
