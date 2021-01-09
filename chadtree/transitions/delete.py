from locale import strxfrm
from os import linesep
from os.path import dirname
from shutil import which
from subprocess import DEVNULL, PIPE, run
from typing import Callable, Iterable, Optional

from pynvim.api import Nvim
from pynvim_pp.lib import s_write

from ..fs.ops import remove, unify_ancestors
from .shared.wm import kill_buffers
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from .shared.index import indices
from ..state.types import State
from ..view.ops import display_path
from .shared.refresh import refresh
from .types import Stage, SysError


def _delete(
    nvim: Nvim,
    state: State,
    settings: Settings,
    is_visual: bool,
    yeet: Callable[[Iterable[str]], None],
) -> Optional[Stage]:
    selection = state.selection or frozenset(
        node.path for node in indices(nvim, state=state, is_visual=is_visual)
    )
    unified = tuple(unify_ancestors(selection))
    if unified:
        display_paths = linesep.join(
            sorted((display_path(path, state=state) for path in unified), key=strxfrm)
        )

        question = LANG("ask_trash", linesep=linesep, display_paths=display_paths)
        resp: int = nvim.funcs.confirm(question, LANG("ask_yesno", linesep=linesep), 2)
        ans = resp == 1
        if ans:
            try:
                yeet(unified)
            except Exception as e:
                s_write(nvim, e, error=True)
                return refresh(nvim, state=state, settings=settings)
            else:
                paths = frozenset(dirname(path) for path in unified)
                new_state = forward(
                    state, settings=settings, selection=frozenset(), paths=paths
                )

                kill_buffers(nvim, paths=selection)
                return Stage(new_state)
        else:
            return None
    else:
        return None


@rpc(blocking=False, name="CHADdelete")
def c_delete(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Delete selected
    """

    return _delete(
        nvim, state=state, settings=settings, is_visual=is_visual, yeet=remove
    )


def _trash(paths: Iterable[str]) -> None:
    if which("trash"):
        ret = run(("trash", *paths), stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE)
        if ret.returncode != 0:
            raise SysError(ret.stderr)
    else:
        raise SysError(LANG("sys_trash_err"))


@rpc(blocking=False, name="CHADtrash")
def c_trash(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Delete selected
    """

    return _delete(
        nvim, state=state, settings=settings, is_visual=is_visual, yeet=_trash
    )
