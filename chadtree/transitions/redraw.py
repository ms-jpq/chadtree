from typing import Optional, Sequence, cast

from pynvim import Nvim
from pynvim_pp.api import cur_win, win_get_cursor, buf_line_count
from pynvim_pp.atomic import Atomic
from pynvim_pp.operators import operator_marks

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

    for win, buf in find_fm_windows(nvim):
        count = buf_line_count(nvim, buf=buf)
        row, col = win_get_cursor(nvim, win=win)
        (r1, c1), (r2, c2) = operator_marks(nvim, buf=buf, visual_type=None)

        if focus_row is not None:
            new_row: Optional[int] = focus_row + 1
        elif win != cwin and current_row is not None:
            new_row = current_row + 1
        elif row >= len(lines):
            new_row = len(lines)
        elif count != len(lines):
            new_row = row + 1
        else:
            new_row = None

        atomic = Atomic()
        atomic.buf_clear_namespace(buf, ns, 0, -1)
        atomic.buf_set_option(buf, "modifiable", True)
        atomic.buf_set_lines(buf, 0, -1, True, lines)
        atomic.buf_set_option(buf, "modifiable", False)

        vtext = cast(Sequence[Sequence[Badge]], badges)
        for idx, bgs in enumerate(vtext):
            vtxt = tuple((badge.text, badge.group) for badge in bgs)
            atomic.buf_set_virtual_text(buf, ns, idx, vtxt, {})

        hl2 = cast(Sequence[Sequence[Highlight]], highlights)
        for idx, hl in enumerate(hl2):
            for h in hl:
                atomic.buf_add_highlight(buf, ns, h.group, idx, h.begin, h.end)

        if new_row is not None:
            atomic.win_set_cursor(win, (new_row, col))

        atomic.call_function("setpos", ("'<", (buf.number, r1 + 1, c1 + 1, 0)))
        atomic.call_function("setpos", ("'>", (buf.number, r2 + 1, c2 + 1, 0)))

        atomic.commit(nvim)
