from locale import strxfrm
from operator import add, sub
from os import linesep
from os.path import dirname, join, relpath
from typing import (
    Callable,
    FrozenSet,
    Iterator,
    Mapping,
    Optional,
    Sequence,
)

from pynvim import Nvim
from pynvim.api.window import Window
from pynvim_pp.lib import s_write

from .fs.cartographer import new as new_root
from .fs.ops import (
    ancestors,
    is_parent,
    new,
    rename,
)
from .fs.types import Mode
from .nvim.quickfix import quickfix
from .nvim.wm import (
    find_current_buffer_name,
    kill_buffers,
    kill_fm_windows,
    resize_fm_windows,
    toggle_fm_window,
    update_buffers,
)
from .registry import autocmd, rpc
from .settings.localization import LANG
from .settings.types import Settings
from .state.ops import dump_session
from .state.next import forward
from .fs.cartographer import is_dir
from .state.types import FilterPattern, Selection, State, VCStatus


def redraw(nvim: Nvim, state: State, focus: Optional[str]) -> None:
    update_buffers(nvim, state=state, focus=focus)


def _current(
    nvim: Nvim, state: State, settings: Settings, current: str
) -> Optional[Stage]:
    if is_parent(parent=state.root.path, child=current):
        paths: FrozenSet[str] = (
            frozenset(ancestors(current)) if state.follow else frozenset()
        )
        index = state.index | paths
        new_state = forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return Stage(new_state)
    else:
        return None


def _change_dir(nvim: Nvim, state: State, settings: Settings, new_base: str) -> Stage:
    index = state.index | {new_base}
    root = new_root(new_base, index=index)
    new_state = forward(state, settings=settings, root=root, index=index)
    return Stage(new_state)


def _refocus(nvim: Nvim, state: State, settings: Settings) -> Stage:
    cwd: str = nvim.funcs.getcwd()
    return _change_dir(nvim, state=state, settings=settings, new_base=cwd)


@rpc(blocking=False, name="CHADrefocus")
def c_changedir(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    return _refocus(nvim, state=state, settings=settings)


autocmd("DirChanged") << f"lua {c_changedir.name}()"


@rpc(blocking=False)
def a_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    current = find_current_buffer_name(nvim)
    if current:
        return _current(nvim, state=state, settings=settings, current=current)
    else:
        return None


autocmd("BufEnter") << f"lua {a_follow.name}()"


@rpc(blocking=False)
def a_session(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Save CHADTree state
    """

    dump_session(state)


autocmd("FocusLost", "ExitPre") << f"lua {a_session.name}()"


@rpc(blocking=False)
def a_quickfix(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Update quickfix list
    """

    qf = quickfix(nvim)
    new_state = forward(state, settings=settings, qf=qf)
    return Stage(new_state)


autocmd("QuickfixCmdPost") << f"lua {a_quickfix.name}()"


@rpc(blocking=False, name="CHADquit")
def c_quit(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Close sidebar
    """

    kill_fm_windows(nvim, settings=settings)


@rpc(blocking=False, name="CHADopen")
def c_open(
    nvim: Nvim, state: State, settings: Settings, args: Sequence[str]
) -> Optional[Stage]:
    """
    Toggle sidebar
    """

    try:
        opts = parse_args(args)
    except ArgparseError as e:
        s_write(nvim, e, error=True)
        return None
    else:
        current = find_current_buffer_name(nvim)
        toggle_fm_window(nvim, state=state, settings=settings, opts=opts)

        stage = _current(nvim, state=state, settings=settings, current=current)
        if stage:
            return stage
        else:
            return Stage(state)


def _resize(
    nvim: Nvim, state: State, settings: Settings, direction: Callable[[int, int], int]
) -> Stage:
    width = max(direction(state.width, 10), 1)
    new_state = forward(state, settings=settings, width=width)

    resize_fm_windows(nvim, width=new_state.width)
    return Stage(new_state)


@rpc(blocking=False, name="CHADbigger")
def c_bigger(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Bigger sidebar
    """
    return _resize(nvim, state=state, settings=settings, direction=add)


@rpc(blocking=False, name="CHADsmaller")
def c_smaller(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Smaller sidebar
    """
    return _resize(nvim, state=state, settings=settings, direction=sub)


@rpc(blocking=False, name="CHADchange_focus")
def c_change_focus(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory
    """

    node = _index(nvim, state=state)
    if node:
        new_base = node.path if Mode.folder in node.mode else dirname(node.path)
        return _change_dir(nvim, state=state, settings=settings, new_base=new_base)
    else:
        return None


@rpc(blocking=False, name="CHADchange_focus_up")
def c_change_focus_up(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory up
    """

    c_root = state.root.path
    parent = dirname(c_root)
    if parent and parent != c_root:
        return _change_dir(nvim, state=state, settings=settings, new_base=parent)
    else:
        return None


@rpc(blocking=False, name="CHADcollapse")
def c_collapse(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Collapse folder
    """

    node = _index(nvim, state=state)
    if node:
        path = node.path if Mode.folder in node.mode else dirname(node.path)
        if path != state.root.path:
            paths = frozenset(
                i for i in state.index if i == path or is_parent(parent=path, child=i)
            )
            index = state.index - paths
            new_state = forward(state, settings=settings, index=index, paths=paths)
            row = new_state.derived.paths_lookup.get(path, 0)
            if row:
                window: Window = nvim.api.get_current_win()
                _, col = nvim.api.win_get_cursor(window)
                nvim.api.win_set_cursor(window, (row + 1, col))

            return Stage(new_state)
        else:
            return None
    else:
        return None


@rpc(blocking=False, name="CHADjump_to_current")
def c_jump_to_current(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Jump to active file
    """

    current = state.current
    if current:
        stage = _current(nvim, state=state, settings=settings, current=current)
        if stage:
            return Stage(state=stage.state, focus=current)
        else:
            return None
    else:
        return None


@rpc(blocking=False, name="CHADtoggle_hidden")
def c_hidden(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Toggle hidden
    """

    new_state = forward(state, settings=settings, show_hidden=not state.show_hidden)
    return Stage(new_state)


@rpc(blocking=False, name="CHADtoggle_follow")
def c_toggle_follow(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Toggle follow
    """

    new_state = forward(state, settings=settings, follow=not state.follow)
    s_write(nvim, LANG("follow_mode_indi", follow=str(new_state.follow)))
    return Stage(new_state)


@rpc(blocking=False, name="CHADtoggle_version_control")
def c_toggle_vc(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Toggle version control
    """

    enable_vc = not state.enable_vc
    vc = _vc_stat(enable_vc)
    new_state = forward(state, settings=settings, enable_vc=enable_vc, vc=vc)
    s_write(nvim, LANG("version_control_indi", enable_vc=str(new_state.enable_vc)))
    return Stage(new_state)


@rpc(blocking=False, name="CHADfilter")
def c_new_filter(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Update filter
    """

    old_p = state.filter_pattern.pattern if state.filter_pattern else ""
    pattern: Optional[str] = nvim.funcs.input(LANG("new_filter"), old_p)
    filter_pattern = FilterPattern(pattern=pattern) if pattern else None
    new_state = forward(
        state, settings=settings, selection=frozenset(), filter_pattern=filter_pattern
    )
    return Stage(new_state)


@rpc(blocking=False, name="CHADsearch")
def c_new_search(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    New search params
    """

    cwd = state.root.path
    pattern: Optional[str] = nvim.funcs.input("new_search", "")
    results = search(pattern or "", cwd=cwd, sep=linesep)
    s_write(nvim, results)

    return Stage(state)


@rpc(blocking=False, name="CHADcopy_name")
def c_copy_name(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy dirname / filename
    """

    def gen_paths() -> Iterator[str]:
        selection = state.selection
        if is_visual or not selection:
            nodes = _indices(nvim, state=state, is_visual=is_visual)
            for node in nodes:
                yield node.path
        else:
            for selected in sorted(selection, key=strxfrm):
                yield selected

    paths = tuple(path for path in gen_paths())

    clip = linesep.join(paths)
    copied_paths = ", ".join(paths)

    nvim.funcs.setreg("+", clip)
    nvim.funcs.setreg("*", clip)
    s_write(nvim, LANG("copy_paths", copied_paths=copied_paths))


@rpc(blocking=False, name="CHADnew")
def c_new(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    new file / folder
    """

    node = _index(nvim, state=state) or state.root
    parent = node.path if is_dir(node) else dirname(node.path)

    child: Optional[str] = nvim.funcs.input(LANG("pencil"))

    if child:
        path = join(parent, child)
        if fs_exists(path):
            s_write(nvim, LANG("already_exists", name=path), error=True)
            return Stage(state)
        else:
            try:
                new(path)
            except Exception as e:
                s_write(nvim, e, error=True)
                return _refresh(nvim, state=state, settings=settings)
            else:
                paths = frozenset(ancestors(path))
                index = state.index | paths
                new_state = forward(state, settings=settings, index=index, paths=paths)
                nxt = _open_file(
                    nvim,
                    state=new_state,
                    settings=settings,
                    path=path,
                    click_type=ClickType.secondary,
                )
                return nxt
    else:
        return None


@rpc(blocking=False, name="CHADrename")
def c_rename(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    rename file / folder
    """

    node = _index(nvim, state=state)
    if node:
        prev_name = node.path
        parent = state.root.path
        rel_path = relpath(prev_name, start=parent)

        child: Optional[str] = nvim.funcs.input(LANG("pencil"), rel_path)
        if child:
            new_name = join(parent, child)
            new_parent = dirname(new_name)
            if fs_exists(new_name):
                s_write(nvim, LANG("already_exists", name=new_name), error=True)
                return Stage(state)
            else:
                try:
                    rename(prev_name, new_name)
                except Exception as e:
                    s_write(nvim, e, error=True)
                    return _refresh(nvim, state=state, settings=settings)
                else:
                    paths = frozenset((parent, new_parent, *ancestors(new_parent)))
                    index = state.index | paths
                    new_state = forward(
                        state, settings=settings, index=index, paths=paths
                    )
                    kill_buffers(nvim, paths=(prev_name,))
                    return Stage(new_state)
        else:
            return None
    else:
        return None


@rpc(blocking=False, name="CHADclear_selection")
def c_clear_selection(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Clear selected
    """

    new_state = forward(state, settings=settings, selection=frozenset())
    return Stage(new_state)


@rpc(blocking=False, name="CHADclear_filter")
def c_clear_filter(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Clear filter
    """

    new_state = forward(state, settings=settings, filter_pattern=None)
    return Stage(new_state)


@rpc(blocking=False, name="CHADselect")
def c_select(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folder / File -> select
    """

    nodes = iter(_indices(nvim, state=state, is_visual=is_visual))
    if is_visual:
        selection = state.selection ^ {n.path for n in nodes}
        new_state = forward(state, settings=settings, selection=selection)
        return Stage(new_state)
    else:
        node = next(nodes, None)
        if node:
            selection = state.selection ^ {node.path}
            new_state = forward(state, settings=settings, selection=selection)
            return Stage(new_state)
        else:
            return None
