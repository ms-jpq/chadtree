from pathlib import PurePath
from typing import Optional, Sequence
from uuid import uuid4

from pynvim import Nvim
from pynvim.api import NvimError
from pynvim.api.buffer import Buffer
from pynvim_pp.api import buf_get_var, buf_line_count, win_get_cursor
from pynvim_pp.atomic import Atomic
from pynvim_pp.operators import operator_marks
from std2.difflib import trans_inplace
from std2.pickle.decoder import new_decoder
from std2.pickle.types import DecodeError

from ..consts import FM_NAMESPACE
from ..state.types import State
from ..view.types import Derived
from .shared.wm import find_fm_windows

_FM_HASH_VAR = f"CHAD_HASH_{uuid4()}"


class UnrecoverableError(Exception):
    ...


_DECODER = new_decoder[Sequence[str]](Sequence[str])


def _update(nvim: Nvim, buf: Buffer, ns: int, derived: Derived) -> Atomic:
    n_hash = derived.hashed
    try:
        p_hash = _DECODER(buf_get_var(nvim, buf=buf, key=_FM_HASH_VAR))
    except DecodeError:
        p_hash = ("",)

    atomic = Atomic()
    for (i1, i2), (j1, j2) in trans_inplace(src=p_hash, dest=n_hash, unifying=10):
        atomic.buf_clear_namespace(buf, ns, i1, i2)
        atomic.buf_set_lines(buf, i1, i2, True, derived.lines[j1:j2])

        for idx, highlights in enumerate(derived.highlights[j1:j2], start=i1):
            for hl in highlights:
                atomic.buf_add_highlight(buf, ns, hl.group, idx, hl.begin, hl.end)

        for idx, badges in enumerate(derived.badges[j1:j2], start=i1):
            vtxt = tuple((bdg.text, bdg.group) for bdg in badges)
            atomic.buf_set_virtual_text(buf, ns, idx, vtxt, {})

    atomic.buf_set_var(buf, _FM_HASH_VAR, n_hash)
    return atomic


def redraw(nvim: Nvim, state: State, focus: Optional[PurePath]) -> None:
    focus_row = state.derived.path_row_lookup.get(focus) if focus else None

    ns = nvim.api.create_namespace(FM_NAMESPACE)

    for win, buf in find_fm_windows(nvim):
        p_count = buf_line_count(nvim, buf=buf)
        n_count = len(state.derived.lines)
        row, col = win_get_cursor(nvim, win=win)
        (r1, c1), (r2, c2) = operator_marks(nvim, buf=buf, visual_type=None)

        if focus_row is not None:
            new_row: Optional[int] = focus_row + 1
        elif row >= n_count:
            new_row = n_count
        elif p_count != n_count:
            new_row = row + 1
        else:
            new_row = None

        a1 = Atomic()
        a1.buf_set_option(buf, "modifiable", True)

        a2 = _update(nvim, buf=buf, ns=ns, derived=state.derived)

        a3 = Atomic()
        a3.buf_set_option(buf, "modifiable", False)
        a3.call_function("setpos", ("'<", (buf.number, r1 + 1, c1 + 1, 0)))
        a3.call_function("setpos", ("'>", (buf.number, r2 + 1, c2 + 1, 0)))
        if new_row is not None:
            a3.win_set_cursor(win, (new_row, col))

        try:
            (a1 + a2 + a3).commit(nvim)
        except NvimError as e:
            raise UnrecoverableError(e)
