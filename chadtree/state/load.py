from pynvim import Nvim
from pynvim_pp.api import get_cwd

from ..fs.cartographer import new
from ..nvim.quickfix import quickfix
from ..settings.types import Settings
from ..view.render import render
from .ops import load_session
from .types import Selection, State, VCStatus


def initial(nvim: Nvim, settings: Settings) -> State:
    cwd = get_cwd(nvim)

    session = load_session(cwd, use_xdg=settings.xdg) if settings.session else None
    index = session.index if session and session.index is not None else {cwd}

    show_hidden = (
        session.show_hidden
        if session and session.show_hidden is not None
        else settings.show_hidden
    )
    enable_vc = (
        session.enable_vc
        if session and session.enable_vc is not None
        else settings.version_ctl.enable
    )

    selection: Selection = set()
    node = new(cwd, index=index)
    qf = quickfix(nvim)
    vc = VCStatus()

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
        enable_vc=enable_vc,
        width=settings.width,
        root=node,
        qf=qf,
        vc=vc,
        current=current,
        derived=derived,
    )
    return state
