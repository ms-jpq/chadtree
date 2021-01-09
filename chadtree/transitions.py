from enum import Enum, auto
from itertools import chain
from locale import strxfrm
from mimetypes import guess_type
from operator import add, sub
from os import linesep
from os.path import basename, dirname, exists, isdir, join, relpath, sep, splitext
from typing import (
    Callable,
    FrozenSet,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
)

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.common import NvimError
from pynvim.api.window import Window
from pynvim_pp.lib import s_write
from std2.types import Void

from .da import human_readable_size
from .fs.cartographer import new as new_root
from .fs.ops import (
    ancestors,
    copy,
    cut,
    fs_exists,
    fs_stat,
    is_parent,
    new,
    remove,
    rename,
    unify_ancestors,
)
from .fs.types import Mode, Node
from .git import status
from .nvim.quickfix import quickfix
from .nvim.wm import (
    find_current_buffer_name,
    is_fm_buffer,
    kill_buffers,
    kill_fm_windows,
    resize_fm_windows,
    show_file,
    toggle_fm_window,
    update_buffers,
)
from .opts import ArgparseError, parse_args
from .registry import autocmd, rpc
from .search import search
from .settings.localization import LANG
from .settings.types import Settings
from .state import dump_session, forward
from .state import index as state_index
from .state import is_dir
from .system import SystemIntegrationError, open_gui, trash
from .types import FilterPattern, Selection, Stage, State, VCStatus


class ClickType(Enum):
    primary = auto()
    secondary = auto()
    tertiary = auto()
    v_split = auto()
    h_split = auto()


def _index(nvim: Nvim, state: State) -> Optional[Node]:
    window: Window = nvim.api.get_current_win()
    buffer: Buffer = nvim.api.win_get_buf(window)
    if is_fm_buffer(nvim, buffer=buffer):
        row, _ = nvim.api.win_get_cursor(window)
        row = row - 1
        return state_index(state, row)
    else:
        return None


def _indices(nvim: Nvim, state: State, is_visual: bool) -> Sequence[Node]:
    def step() -> Iterator[Node]:
        if is_visual:
            buffer: Buffer = nvim.api.get_current_buf()
            r1, _ = nvim.api.buf_get_mark(buffer, "<")
            r2, _ = nvim.api.buf_get_mark(buffer, ">")
            for row in range(r1 - 1, r2):
                node = state_index(state, row)
                if node:
                    yield node
        else:
            window: Window = nvim.api.get_current_win()
            row, _ = nvim.api.win_get_cursor(window)
            row = row - 1
            node = state_index(state, row)
            if node:
                yield node

    return tuple(step())


def redraw(nvim: Nvim, state: State, focus: Optional[str]) -> None:
    update_buffers(nvim, state=state, focus=focus)


def _display_path(path: str, state: State) -> str:
    raw = relpath(path, start=state.root.path)
    name = raw.replace(linesep, r"\n")
    if isdir(path):
        return f"{name}{sep}"
    else:
        return name


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


def _open_file(
    nvim: Nvim, state: State, settings: Settings, path: str, click_type: ClickType
) -> Optional[Stage]:
    name = basename(path)
    _, ext = splitext(name)
    mime, _ = guess_type(name, strict=False)
    m_type, _, _ = (mime or "").partition("/")

    def ask() -> bool:
        question = LANG("mime_warn", name=name, mime=str(mime))
        resp: int = nvim.funcs.confirm(question, LANG("ask_yesno", linesep=linesep), 2)
        return resp == 1

    ans = (
        ask()
        if m_type in settings.mime.warn and ext not in settings.mime.ignore_exts
        else True
    )
    if ans:
        new_state = forward(state, settings=settings, current=path)
        show_file(nvim, state=new_state, settings=settings, click_type=click_type)
        return Stage(new_state)
    else:
        return None


def _click(
    nvim: Nvim, state: State, settings: Settings, click_type: ClickType
) -> Optional[Stage]:
    node = _index(nvim, state=state)

    if node:
        if Mode.orphan_link in node.mode:
            name = node.name
            s_write(nvim, LANG("dead_link", name=name), error=True)
            return None
        else:
            if Mode.folder in node.mode:
                if state.filter_pattern:
                    s_write(nvim, LANG("filter_click"))
                    return None
                else:
                    paths = frozenset((node.path,))
                    index = state.index ^ paths
                    new_state = forward(
                        state, settings=settings, index=index, paths=paths
                    )
                    return Stage(new_state)
            else:
                nxt = _open_file(
                    nvim,
                    state=state,
                    settings=settings,
                    path=node.path,
                    click_type=click_type,
                )
                return nxt
    else:
        return None


@rpc(blocking=False, name="CHADprimary")
def c_primary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.primary)


@rpc(blocking=False, name="CHADsecondary")
def c_secondary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> preview
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.secondary)


@rpc(blocking=False, name="CHADtertiary")
def c_tertiary(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in new tab
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.tertiary)


@rpc(blocking=False, name="CHADv_split")
def c_v_split(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in vertical split
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.v_split)


@rpc(blocking=False, name="CHADh_split")
def c_h_split(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in horizontal split
    """

    return _click(nvim, state=state, settings=settings, click_type=ClickType.h_split)


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


def _vc_stat(enable: bool) -> VCStatus:
    if enable:
        return status()
    else:
        return VCStatus()


def _refresh(
    nvim: Nvim, state: State, settings: Settings, write_out: bool = False
) -> Stage:
    """
    Redraw buffers
    """

    if write_out:
        s_write(nvim, LANG("hourglass"))

    current = find_current_buffer_name(nvim)
    cwd = state.root.path
    paths = frozenset((cwd,))
    new_current = current if is_parent(parent=cwd, child=current) else None

    index = frozenset(i for i in state.index if exists(i)) | paths
    selection: Selection = (
        frozenset()
        if state.filter_pattern
        else frozenset(s for s in state.selection if exists(s))
    )
    current_paths: FrozenSet[str] = (
        frozenset(ancestors(current)) if state.follow else frozenset()
    )
    new_index = index if new_current else index | current_paths

    qf, vc = quickfix(nvim), _vc_stat(state.enable_vc)
    new_state = forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        qf=qf,
        vc=vc,
        paths=paths,
        current=new_current or Void,
    )

    if write_out:
        s_write(nvim, LANG("ok_sym"))

    return Stage(new_state)


@rpc(blocking=False)
def a_schedule_update(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    try:
        return _refresh(nvim, state=state, settings=settings, write_out=False)
    except NvimError:
        return None


autocmd("BufWritePost", "FocusGained") << f"lua {a_schedule_update.name}()"


@rpc(blocking=False, name="CHADrefresh")
def c_refresh(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    return _refresh(nvim, state=state, settings=settings, write_out=True)


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


@rpc(blocking=False, name="CHADstat")
def c_stat(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Print file stat to cmdline
    """

    node = _index(nvim, state=state)
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
            name = node.name + sep if Mode.folder in node.mode else node.name
            full_name = f"{name} -> {stat.link}" if stat.link else name
            mode_line = f"{permissions} {size} {user} {group} {mtime} {full_name}"
            s_write(nvim, mode_line)


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


def _delete(
    nvim: Nvim,
    state: State,
    settings: Settings,
    is_visual: bool,
    yeet: Callable[[Iterable[str]], None],
) -> Optional[Stage]:
    selection = state.selection or frozenset(
        node.path for node in _indices(nvim, state=state, is_visual=is_visual)
    )
    unified = tuple(unify_ancestors(selection))
    if unified:
        display_paths = linesep.join(
            sorted((_display_path(path, state=state) for path in unified), key=strxfrm)
        )

        question = LANG("ask_trash", linesep=linesep, display_paths=display_paths)
        resp: int = nvim.funcs.confirm(question, LANG("ask_yesno", linesep=linesep), 2)
        ans = resp == 1
        if ans:
            try:
                yeet(unified)
            except Exception as e:
                s_write(nvim, e, error=True)
                return _refresh(nvim, state=state, settings=settings)
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


@rpc(blocking=False, name="CHADtrash")
def c_trash(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Delete selected
    """

    return _delete(
        nvim, state=state, settings=settings, is_visual=is_visual, yeet=trash
    )


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
    op_name: str,
    action: Callable[[Mapping[str, str]], None],
) -> Optional[Stage]:
    node = _index(nvim, state=state)
    selection = state.selection
    unified = tuple(unify_ancestors(selection))
    if unified and node:
        pre_operations = {src: _find_dest(src, node) for src in unified}
        pre_existing = {s: d for s, d in pre_operations.items() if exists(d)}
        new_operations: MutableMapping[str, str] = {}
        while pre_existing:
            source, dest = pre_existing.popitem()
            resp: Optional[str] = nvim.funcs.input(LANG("path_exists_err"), dest)
            if not resp:
                break
            elif exists(resp):
                pre_existing[source] = resp
            else:
                new_operations[source] = resp

        if pre_existing:
            msg = ", ".join(
                f"{_display_path(s, state=state)} -> {_display_path(d, state=state)}"
                for s, d in sorted(pre_existing.items(), key=lambda t: strxfrm(t[0]))
            )
            s_write(
                nvim, f"⚠️  -- {op_name}: path(s) already exist! :: {msg}", error=True
            )
            return None
        else:
            operations: Mapping[str, str] = {**pre_operations, **new_operations}
            msg = linesep.join(
                f"{_display_path(s, state=state)} -> {_display_path(d, state=state)}"
                for s, d in sorted(operations.items(), key=lambda t: strxfrm(t[0]))
            )

            question = f"{op_name}{linesep}{msg}?"
            resp = nvim.funcs.confirm(question, LANG("ask_yesno", linesep=linesep), 2)
            ans = resp == 1

            if ans:
                try:
                    action(operations)
                except Exception as e:
                    s_write(nvim, e, error=True)
                    return _refresh(nvim, state=state, settings=settings)
                else:
                    paths = frozenset(
                        dirname(p)
                        for p in chain(operations.keys(), operations.values())
                    )
                    index = state.index | paths
                    new_state = forward(
                        state,
                        settings=settings,
                        index=index,
                        selection=frozenset(),
                        paths=paths,
                    )

                    kill_buffers(nvim, paths=selection)
                    return Stage(new_state)
            else:
                return None
    else:
        s_write(nvim, LANG("nothing_select"), error=True)
        return None


@rpc(blocking=False, name="CHADcut")
def c_cut(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Cut selected
    """

    return _operation(
        nvim, state=state, settings=settings, op_name=LANG("cut"), action=cut
    )


@rpc(blocking=False, name="CHADcopy")
def c_copy(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Copy selected
    """

    return _operation(
        nvim, state=state, settings=settings, op_name=LANG("copy"), action=copy
    )


@rpc(blocking=False, name="CHADopen_sys")
def c_open_system(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> None:
    """
    Open using finder / dolphin, etc
    """

    node = _index(nvim, state=state)
    if node:
        try:
            open_gui(node.path)
        except SystemIntegrationError as e:
            s_write(nvim, e)
