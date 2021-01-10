from pynvim import Nvim
from pynvim_pp.lib import s_write

from ..da import human_readable_size
from ..fs.ops import fs_stat
from ..registry import rpc
from ..settings.types import Settings
from .shared.index import indices
from ..state.types import State
from ..view.ops import display_path


@rpc(blocking=False, name="CHADstat")
def c_stat(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Print file stat to cmdline
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if node:
        try:
            stat = fs_stat(node.path)
        except Exception as e:
            s_write(nvim, e, error=True)
        else:
            permissions = stat.permissions
            size = human_readable_size(stat.size, truncate=2)
            user = stat.user
            group = stat.group
            mtime = format(stat.date_mod, settings.view.time_fmt)
            name = display_path(node.path, state=state)
            full_name = f"{name} -> {stat.link}" if stat.link else name
            mode_line = f"{permissions} {size} {user} {group} {mtime} {full_name}"
            s_write(nvim, mode_line)
