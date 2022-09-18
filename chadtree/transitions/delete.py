from locale import strxfrm
from os import linesep
from pathlib import PurePath
from subprocess import CalledProcessError
from typing import Awaitable, Callable, Iterable, Optional

from pynvim_pp.nvim import Nvim
from std2.asyncio.subprocess import call

from ..fs.ops import ancestors, remove, unify_ancestors
from ..lsp.notify import lsp_removed
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..view.ops import display_path
from .open_system import which
from .shared.index import indices
from .shared.refresh import refresh
from .shared.wm import kill_buffers
from .types import Stage


async def _remove(
    state: State,
    settings: Settings,
    is_visual: bool,
    yeet: Callable[[Iterable[PurePath]], Awaitable[None]],
) -> Optional[Stage]:
    cwd, root = await Nvim.getcwd(), state.root.path
    nono = {cwd, root} | ancestors(cwd) | ancestors(root)

    selection = state.selection or {
        node.path async for node in indices(state, is_visual=is_visual)
    }
    unified = unify_ancestors(selection)

    if not unified:
        return None
    elif not unified.isdisjoint(nono):
        await Nvim.write(LANG("operation not permitted on root"), error=True)
        return None
    else:
        display_paths = linesep.join(
            sorted((display_path(path, state=state) for path in unified), key=strxfrm)
        )

        question = LANG("ask_trash", display_paths=display_paths)
        ans = await Nvim.confirm(
            question=question,
            answers=LANG("ask_yesno"),
            answer_key={1: True, 2: False},
        )

        if not ans:
            return None
        else:
            try:
                await yeet(unified)
            except Exception as e:
                await Nvim.write(e, error=True)
                return await refresh(state, settings=settings)
            else:
                paths = {path.parent for path in unified}
                new_state = await forward(
                    state, settings=settings, selection=set(), paths=paths
                )

                await kill_buffers(
                    last_used=new_state.window_order, paths=selection, reopen={}
                )
                await lsp_removed(unified)
                return Stage(new_state)


@rpc(blocking=False)
async def _delete(state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    Delete selected
    """

    return await _remove(state, settings=settings, is_visual=is_visual, yeet=remove)


async def _sys_trash(paths: Iterable[PurePath]) -> None:
    cwd = await Nvim.getcwd()

    if arg0 := which("trash"):
        try:
            await call(arg0, "--", *map(str, paths), cwd=cwd)
        except CalledProcessError as e:
            await Nvim.write(e, e.stderr, e.stdout, error=True)

    else:
        await Nvim.write(LANG("sys_trash_err"), error=True)


@rpc(blocking=False)
async def _trash(state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    Delete selected
    """

    return await _remove(
        state,
        settings=settings,
        is_visual=is_visual,
        yeet=_sys_trash,
    )
