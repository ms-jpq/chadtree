from typing import Optional, Sequence, cast

from pynvim import Nvim
from pynvim_pp.api import cur_win, win_get_cursor
from pynvim_pp.atomic import Atomic

from ..consts import FM_NAMESPACE
from ..state.types import State
from ..view.types import Badge, Highlight
from .shared.wm import find_fm_windows


def redraw(nvim: Nvim, state: State, focus: Optional[str]) -> None:
    focus_row = state.derived.paths_lookup.get(focus) if focus else None
    current = state.current
    current_row = state.derived.paths_lookup.get(current or "")
    lines, badges, highlights = zip(
        *(
            (render.line, render.badges, render.highlights)
            for render in state.derived.rendered
        )
    )
    cwin = cur_win(nvim)
    ns = nvim.api.create_namespace(FM_NAMESPACE)

    for win, buffer in find_fm_windows(nvim):
        row, col = win_get_cursor(nvim, win=win)
        new_row = (
            focus_row + 1
            if focus_row is not None
            else (
                current_row + 1
                if win.number != cwin.number and current_row is not None
                else min(row + 1, len(lines))
            )
        )

        atomic = Atomic()
        atomic.buf_clear_namespace(buffer, ns, 0, -1)
        atomic.buf_set_option(buffer, "modifiable", True)
        atomic.buf_set_lines(buffer, 0, -1, True, lines)
        atomic.buf_set_option(buffer, "modifiable", False)

        vtext = cast(Sequence[Sequence[Badge]], badges)
        for idx, bgs in enumerate(vtext):
            vtxt = tuple((badge.text, badge.group) for badge in bgs)
            atomic.buf_set_virtual_text(buffer, ns, idx, vtxt, {})

        hl2 = cast(Sequence[Sequence[Highlight]], highlights)
        for idx, hl in enumerate(hl2):
            for h in hl:
                atomic.buf_add_highlight(buffer, ns, h.group, idx, h.begin, h.end)

        atomic.win_set_cursor(win, (new_row, col))
        atomic.commit(nvim)
