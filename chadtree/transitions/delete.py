from locale import strxfrm
from os import linesep
from os.path import dirname
from shutil import which
from subprocess import DEVNULL, PIPE, CalledProcessError, check_call
from typing import Callable, Iterable, Optional

from pynvim.api import Nvim
from pynvim_pp.api import ask_mc, get_cwd
from pynvim_pp.lib import threadsafe_call, write
from pynvim_pp.logging import log

from ..fs.ops import ancestors, remove, unify_ancestors
from ..registry import enqueue_event, pool, rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..view.ops import display_path
from .refresh import refresh as _refresh
from .shared.index import indices
from .shared.refresh import refresh
from .shared.wm import kill_buffers, find_non_fm_windows_in_tab
from .types import Stage


def _remove(
    nvim: Nvim,
    state: State,
    settings: Settings,
    is_visual: bool,
    yeet: Callable[[Iterable[str]], None],
) -> Optional[Stage]:
    cwd, root = get_cwd(nvim), state.root.path
    nono = {cwd, root} | ancestors(cwd) | ancestors(root)

    selection = state.selection or {
        node.path for node in indices(nvim, state=state, is_visual=is_visual)
    }
    unified = unify_ancestors(selection)

    if not unified:
        return None
    elif not unified.isdisjoint(nono):
        write(nvim, LANG("operation not permitted on root"), error=True)
        return None
    else:
        display_paths = linesep.join(
            sorted((display_path(path, state=state) for path in unified), key=strxfrm)
        )

        question = LANG("ask_trash", display_paths=display_paths)
        ans = ask_mc(
            nvim,
            question=question,
            answers=LANG("ask_yesno"),
            answer_key={1: True, 2: False},
        )

        if not ans:
            return None
        else:
            try:
                yeet(unified)
            except Exception as e:
                write(nvim, e, error=True)
                return refresh(nvim, state=state, settings=settings)
            else:
                paths = {dirname(path) for path in unified}
                new_state = forward(
                    state, settings=settings, selection=set(), paths=paths
                )

                kill_buffers(nvim, paths=selection)
                return Stage(new_state)


@rpc(blocking=False)
def _delete(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Delete selected
    """

    return _remove(
        nvim, state=state, settings=settings, is_visual=is_visual, yeet=remove
    )


def _sys_trash(nvim: Nvim) -> Callable[[Iterable[str]], None]:
    cwd = get_cwd(nvim)

    def cont(paths: Iterable[str]) -> None:
        def c1() -> None:
            cmd = "trash"
            if which(cmd):
                command = (cmd, "--", *paths)
                check_call(command, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, cwd=cwd)
            else:
                raise LookupError(LANG("sys_trash_err"))

        def c2() -> None:
            try:
                c1()
            except (CalledProcessError, LookupError) as e:
                threadsafe_call(nvim, write, nvim, e, error=True)
            except Exception as e:
                log.exception("%s", e)
            else:
                enqueue_event(_refresh, True)

        pool.submit(c2)

    return cont


@rpc(blocking=False)
def _trash(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Delete selected
    """

    return _remove(
        nvim, state=state, settings=settings, is_visual=is_visual, yeet=_sys_trash(nvim)
    )
