from pynvim import Nvim
from pynvim_pp.lib import write

from ..da import human_readable_size
from ..fs.ops import fs_stat
from ..registry import rpc
from ..settings.types import Settings
from .shared.index import indices
from ..state.types import State
from ..view.ops import display_path


@rpc(blocking=False)
def _stat(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Print file stat to cmdline
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        try:
            stat = fs_stat(node.path)
        except Exception as e:
            write(nvim, e, error=True)
        else:
            permissions = stat.permissions
            size = human_readable_size(stat.size, precision=2)
            user = stat.user
            group = stat.group
            mtime = stat.date_mod.strftime(settings.view.time_fmt)
            name = display_path(node.path, state=state)
            full_name = f"{name} -> {stat.link}" if stat.link else name
            mode_line = f"{permissions} {size}b {user} {group} {mtime} {full_name}"
            write(nvim, mode_line)
