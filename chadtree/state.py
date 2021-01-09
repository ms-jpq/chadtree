from hashlib import sha1
from pathlib import Path
from typing import FrozenSet, Optional, Union, cast

from pynvim import Nvim
from std2.pickle import decode, encode
from std2.types import Void, VoidType, or_else
from dataclasses import dataclass
from .fs.cartographer import new, update
from .consts import SESSION_DIR
from .da import dump_json, load_json
from .git import status
from .nvim import getcwd
from .quickfix import quickfix
from .view.render import render
from .types import (
    FilterPattern,
    Index,
    QuickFix,
    Selection,
    State,
    VCStatus,
)
from .fs.types import Node, Mode
from .settings.types import Settings

@dataclass(frozen=True)
class _Session:
    index: Index
    show_hidden: bool


def _session_path(cwd: str) -> Path:
    hashed = sha1(cwd.encode()).hexdigest()
    part = SESSION_DIR / hashed
    return part.with_suffix(".json")


def load_session(cwd: str) -> _Session:
    load_path = _session_path(cwd)
    try:
        return decode(_Session, load_json(load_path))
    except Exception:
        return _Session(index=frozenset((cwd,)), show_hidden=False)


def dump_session(state: State) -> None:
    load_path = _session_path(state.root.path)
    json = _Session(index=state.index, show_hidden=state.show_hidden)
    dump_json(load_path, encode(json))


def initial(nvim: Nvim, settings: Settings) -> State:
    version_ctl = settings.version_ctl
    cwd = getcwd(nvim)

    session = load_session(cwd)
    index = session.index if settings.session else frozenset((cwd,))
    show_hidden = session.show_hidden if settings.session else settings.show_hidden

    selection: Selection = frozenset()
    node, qf = new(cwd, index=index), quickfix(nvim)
    vc = VCStatus() if not version_ctl.enable or version_ctl.defer else status()

    current = None
    filter_pattern = None

    derived = render(
        node,
        settings=settings,
        index=index,
        selection=selection,
        filter_pattern=filter_pattern,
        qf=qf,
        vc=vc,
        show_hidden=show_hidden,
        current=current,
    )

    state = State(
        index=index,
        selection=selection,
        filter_pattern=filter_pattern,
        show_hidden=show_hidden,
        follow=settings.follow,
        enable_vc=settings.version_ctl.enable,
        width=settings.width,
        root=node,
        qf=qf,
        vc=vc,
        current=current,
        derived=derived,
    )
    return state


def forward(
    state: State,
    *,
    settings: Settings,
    root: Union[Node, VoidType] = Void,
    index: Union[Index, VoidType] = Void,
    selection: Union[Selection, VoidType] = Void,
    filter_pattern: Union[Optional[FilterPattern], VoidType] = Void,
    show_hidden: Union[bool, VoidType] = Void,
    follow: Union[bool, VoidType] = Void,
    enable_vc: Union[bool, VoidType] = Void,
    width: Union[int, VoidType] = Void,
    qf: Union[QuickFix, VoidType] = Void,
    vc: Union[VCStatus, VoidType] = Void,
    current: Union[str, VoidType] = Void,
    paths: Union[FrozenSet[str], VoidType] = Void,
) -> State:
    new_index = or_else(index, state.index)
    new_selection = or_else(selection, state.selection)
    new_filter_pattern = or_else(filter_pattern, state.filter_pattern)
    new_current = or_else(current, state.current)
    new_root = cast(
        Node,
        root
        or (
            update(state.root, index=new_index, paths=cast(FrozenSet[str], paths))
            if paths
            else state.root
        ),
    )
    new_qf = or_else(qf, state.qf)
    new_vc = or_else(vc, state.vc)
    new_hidden = or_else(show_hidden, state.show_hidden)
    derived = render(
        new_root,
        settings=settings,
        index=new_index,
        selection=new_selection,
        filter_pattern=new_filter_pattern,
        qf=new_qf,
        vc=new_vc,
        show_hidden=new_hidden,
        current=new_current,
    )

    new_state = State(
        index=new_index,
        selection=new_selection,
        filter_pattern=new_filter_pattern,
        show_hidden=new_hidden,
        follow=or_else(follow, state.follow),
        enable_vc=or_else(enable_vc, state.enable_vc),
        width=or_else(width, state.width),
        root=new_root,
        qf=new_qf,
        vc=new_vc,
        current=new_current,
        derived=derived,
    )

    return new_state


def index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.derived.lookup)):
        return state.derived.lookup[row]
    else:
        return None


def is_dir(node: Node) -> bool:
    return Mode.folder in node.mode
