from concurrent.futures import Executor
from itertools import chain
from locale import strxfrm
from os import linesep
from pathlib import PurePath
from typing import AbstractSet, Callable, Mapping, MutableMapping, Optional

from pynvim.api import Nvim
from pynvim_pp.api import ask, ask_mc, get_cwd
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, copy, cut, exists, unify_ancestors
from ..fs.types import Node
from ..lsp.notify import lsp_created, lsp_moved
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..view.ops import display_path
from .shared.index import indices
from .shared.refresh import refresh
from .shared.wm import kill_buffers
from .types import Stage


def _find_dest(src: PurePath, node: Node) -> PurePath:
    parent = node.path if is_dir(node) else node.path.parent
    dst = parent / src.name
    return dst


def _operation(
    nvim: Nvim,
    *,
    state: State,
    settings: Settings,
    is_visual: bool,
    nono: AbstractSet[PurePath],
    op_name: str,
    is_move: bool,
    action: Callable[[Executor, Mapping[PurePath, PurePath]], None],
) -> Optional[Stage]:
    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    selection = state.selection
    unified = unify_ancestors(selection)

    if not unified or not node:
        write(nvim, LANG("nothing_select"), error=True)
        return None
    elif not unified.isdisjoint(nono):
        write(nvim, LANG("operation not permitted on root"), error=True)
        return None
    else:
        pre_operations = {src: _find_dest(src, node) for src in unified}
        pre_existing = {
            s: d for s, d in pre_operations.items() if exists(d, follow=False)
        }

        new_operations: MutableMapping[PurePath, PurePath] = {}
        while pre_existing:
            source, dest = pre_existing.popitem()
            resp = ask(nvim, question=LANG("path_exists_err"), default=dest.name)
            new_dest = dest.parent / resp if resp else None

            if not new_dest:
                pre_existing[source] = dest
                break
            elif exists(new_dest, follow=False):
                pre_existing[source] = new_dest
            else:
                new_operations[source] = new_dest

        if pre_existing:
            msg = linesep.join(
                f"{display_path(s, state=state)} -> {display_path(d, state=state)}"
                for s, d in sorted(
                    pre_existing.items(), key=lambda t: strxfrm(str(t[0]))
                )
            )
            write(
                nvim,
                LANG("paths already exist", operation=op_name, paths=msg),
                error=True,
            )
            return None

        else:
            operations = {**pre_operations, **new_operations}
            msg = linesep.join(
                f"{display_path(s, state=state)} -> {display_path(d, state=state)}"
                for s, d in sorted(operations.items(), key=lambda t: strxfrm(str(t[0])))
            )

            question = LANG("confirm op", operation=op_name, paths=msg)
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
                    action(state.pool, operations)
                except Exception as e:
                    write(nvim, e, error=True)
                    return refresh(nvim, state=state, settings=settings)
                else:
                    paths = {
                        p.parent for p in chain(operations.keys(), operations.values())
                    }
                    index = state.index | paths
                    new_selection = {*operations.values()}
                    new_state = forward(
                        state,
                        settings=settings,
                        index=index,
                        selection=new_selection,
                        paths=paths,
                    )
                    focus = next(
                        iter(
                            sorted(
                                new_selection,
                                key=lambda p: tuple(map(strxfrm, p.parts)),
                            ),
                        ),
                        None,
                    )

                    if is_move:
                        kill_buffers(
                            nvim,
                            last_used=new_state.window_order,
                            paths=selection,
                            reopen={},
                        )
                        lsp_moved(nvim, paths=operations)
                    else:
                        lsp_created(nvim, paths=new_selection)
                    return Stage(new_state, focus=focus)


@rpc(blocking=False)
def _cut(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Cut selected
    """

    cwd, root = get_cwd(nvim), state.root.path
    nono = {cwd, root} | ancestors(cwd) | ancestors(root)
    return _operation(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        nono=nono,
        op_name=LANG("cut"),
        action=cut,
        is_move=True,
    )


@rpc(blocking=False)
def _copy(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Copy selected
    """

    return _operation(
        nvim,
        state=state,
        settings=settings,
        is_visual=is_visual,
        nono=set(),
        op_name=LANG("copy"),
        action=copy,
        is_move=False,
    )
