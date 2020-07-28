from asyncio import gather
from hashlib import sha1
from os.path import exists, join
from typing import Optional, Sequence

from pynvim import Nvim

from .cartographer import new, update
from .consts import session_dir
from .da import dump_json, load_json, or_else
from .git import status
from .nvim import getcwd
from .quickfix import quickfix
from .render import render
from .types import (
    Index,
    Mode,
    Node,
    QuickFix,
    Selection,
    Session,
    Set,
    Settings,
    State,
    VCStatus,
)


def session_path(cwd: str) -> str:
    hashed = sha1(cwd.encode()).hexdigest()
    part = join(session_dir, hashed)
    return f"{part}.json"


def load_session(cwd: str) -> Index:
    load_path = session_path(cwd)
    if exists(load_path):
        try:
            json = load_json(load_path)
        except Exception:
            return {cwd}
        else:
            session = Session(index=json["index"])
            return {*session.index}
    else:
        return {cwd}


def dump_session(state: State) -> None:
    load_path = session_path(state.root.path)
    session = Session(index=state.index)
    json = {"index": [*session.index]}
    dump_json(load_path, json)


async def initial(nvim: Nvim, settings: Settings) -> State:
    cwd = await getcwd(nvim)
    index = load_session(cwd) if settings.session else {cwd}
    selection: Selection = set()
    node, qf = await gather(new(cwd, index=index), quickfix(nvim))
    vc = VCStatus() if settings.version_ctl.defer else await status()
    current = None
    lookup, rendered = render(
        node,
        settings=settings,
        index=index,
        selection=selection,
        qf=qf,
        vc=vc,
        show_hidden=settings.show_hidden,
        current=current,
    )

    state = State(
        index=index,
        selection=selection,
        show_hidden=settings.show_hidden,
        follow=settings.follow,
        width=settings.width,
        root=node,
        qf=qf,
        vc=vc,
        current=current,
        lookup=lookup,
        rendered=rendered,
    )
    return state


async def forward(
    state: State,
    *,
    settings: Settings,
    root: Optional[Node] = None,
    index: Optional[Index] = None,
    selection: Optional[Selection] = None,
    show_hidden: Optional[bool] = None,
    follow: Optional[bool] = None,
    width: Optional[int] = None,
    qf: Optional[QuickFix] = None,
    vc: Optional[VCStatus] = None,
    current: Optional[str] = None,
    paths: Optional[Set[str]] = None,
) -> State:
    new_index = or_else(index, state.index)
    new_selection = or_else(selection, state.selection)
    new_current = or_else(current, state.current)
    new_root = root or (
        await update(state.root, index=new_index, paths=paths) if paths else state.root
    )
    new_qf = or_else(qf, state.qf)
    new_vc = or_else(vc, state.vc)
    new_hidden = or_else(show_hidden, state.show_hidden)
    lookup, rendered = render(
        new_root,
        settings=settings,
        index=new_index,
        selection=new_selection,
        qf=new_qf,
        vc=new_vc,
        show_hidden=new_hidden,
        current=new_current,
    )

    new_state = State(
        index=new_index,
        selection=new_selection,
        show_hidden=new_hidden,
        follow=or_else(follow, state.follow),
        width=or_else(width, state.width),
        root=new_root,
        qf=new_qf,
        vc=new_vc,
        current=new_current,
        lookup=lookup,
        rendered=rendered,
    )

    return new_state


def index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.lookup)):
        return state.lookup[row]
    else:
        return None


def is_dir(node: Node) -> bool:
    return Mode.FOLDER in node.mode
