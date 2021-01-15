from pynvim import Nvim
from pynvim_pp.api import get_cwd

from ..fs.cartographer import new
from ..nvim.quickfix import quickfix
from ..settings.types import Settings
from ..version_ctl.git import status
from ..view.render import render
from .ops import load_session
from .types import Selection, State, VCStatus


def initial(nvim: Nvim, settings: Settings) -> State:
    version_ctl = settings.version_ctl
    cwd = get_cwd(nvim)

    session = load_session(cwd)
    index = session.index if settings.session else {cwd}
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
