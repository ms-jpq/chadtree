from asyncio import gather
from pathlib import Path

from pynvim_pp.nvim import Nvim

from ..consts import SESSION_DIR
from ..fs.cartographer import new
from ..nvim.markers import markers
from ..settings.types import Settings
from ..version_ctl.types import VCStatus
from ..view.render import render
from .ops import load_session
from .types import Selection, Session, State


async def initial(settings: Settings) -> State:
    cwd, marks = await gather(Nvim.getcwd(), markers())
    storage = (
        Path(await Nvim.fn.stdpath(str, "cache")) / "chad_sessions"
        if settings.xdg
        else SESSION_DIR
    )

    session = Session(workdir=cwd, storage=storage)
    stored = await load_session(session) if settings.session else None
    index = {cwd} | (stored.index if stored else frozenset())
    bookmarks = stored.bookmarks if stored else {}

    show_hidden = (
        stored.show_hidden
        if stored and stored.show_hidden is not None
        else settings.show_hidden
    )
    enable_vc = (
        stored.enable_vc
        if stored and stored.enable_vc is not None
        else settings.version_ctl.enable
    )

    selection: Selection = frozenset()
    node = await new(cwd, index=index)
    vc = VCStatus()

    current = None
    filter_pattern = None

    derived = render(
        node,
        settings=settings,
        index=index,
        bookmarks=bookmarks,
        selection=selection,
        filter_pattern=filter_pattern,
        markers=marks,
        vc=vc,
        show_hidden=show_hidden,
        current=current,
    )

    state = State(
        session=session,
        index=index,
        bookmarks=bookmarks,
        selection=selection,
        filter_pattern=filter_pattern,
        show_hidden=show_hidden,
        follow=settings.follow,
        enable_vc=enable_vc,
        width=settings.width,
        root=node,
        markers=marks,
        vc=vc,
        current=current,
        derived=derived,
        window_order={},
    )
    return state
