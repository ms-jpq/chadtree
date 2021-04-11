from itertools import chain
from locale import strxfrm
from os import linesep
from os.path import basename, dirname, exists, join
from typing import AbstractSet, Callable, Mapping, MutableMapping, Optional

from pynvim.api import Nvim
from pynvim_pp.api import ask, ask_mc, get_cwd
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, copy, cut, unify_ancestors
from ..fs.types import Node
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


def _find_dest(src: str, node: Node) -> str:
    name = basename(src)
    parent = node.path if is_dir(node) else dirname(node.path)
    dst = join(parent, name)
    return dst


def _operation(
    nvim: Nvim,
    *,
    state: State,
    settings: Settings,
    is_visual: bool,
    nono: AbstractSet[str],
    op_name: str,
    kill_buffs: bool,
    action: Callable[[Mapping[str, str]], None],
) -> Optional[Stage]:

    root = state.root.path
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
        pre_existing = {s: d for s, d in pre_operations.items() if exists(d)}

        new_operations: MutableMapping[str, str] = {}
        while pre_existing:
            source, dest = pre_existing.popitem()
            rel_dest = display_path(dest, state=state)
            resp = ask(nvim, question=LANG("path_exists_err"), default=rel_dest)

            new_dest = join(root, resp) if resp else None

            if not new_dest:
                pre_existing[source] = dest
                break
            elif exists(new_dest):
                pre_existing[source] = new_dest
            else:
                new_operations[source] = new_dest

        if pre_existing:
            msg = linesep.join(
                f"{display_path(s, state=state)} -> {display_path(d, state=state)}"
                for s, d in sorted(pre_existing.items(), key=lambda t: strxfrm(t[0]))
            )
            write(
                nvim,
                LANG("paths already exist", operation=op_name, paths=msg),
                error=True,
            )
            return None

        else:
            operations: Mapping[str, str] = {**pre_operations, **new_operations}
            msg = linesep.join(
                f"{display_path(s, state=state)} -> {display_path(d, state=state)}"
                for s, d in sorted(operations.items(), key=lambda t: strxfrm(t[0]))
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
                    action(operations)
                except Exception as e:
                    write(nvim, e, error=True)
                    return refresh(nvim, state=state, settings=settings)
                else:
                    paths = {
                        dirname(p)
                        for p in chain(operations.keys(), operations.values())
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

                    if kill_buffs:
                        kill_buffers(nvim, paths=selection)
                    return Stage(new_state)


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
        kill_buffs=True,
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
        kill_buffs=False,
    )
