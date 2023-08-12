from pathlib import Path, PurePath
from typing import Optional, Sequence
from uuid import uuid4

from pynvim_pp.atomic import Atomic
from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Nvim
from pynvim_pp.operators import operator_marks
from pynvim_pp.rpc_types import NvimError
from pynvim_pp.types import NoneType
from pynvim_pp.window import Window
from std2.difflib import trans_inplace
from std2.pickle.decoder import new_decoder
from std2.pickle.types import DecodeError

from ..consts import URI_SCHEME
from ..state.types import State
from ..view.types import Derived
from .shared.wm import find_fm_windows


class UnrecoverableError(Exception):
    ...


_NS = uuid4()
_LUA = (Path(__file__).resolve(strict=True).parent / "winline.lua").read_text("UTF-8")


_DECODER = new_decoder[Sequence[str]](Sequence[str])


def _update(
    use_extmarks: bool,
    buf: Buffer,
    ns: int,
    derived: Derived,
    hashed_lines: Sequence[str],
) -> Atomic:
    atomic = Atomic()
    for (i1, i2), (j1, j2) in trans_inplace(
        src=hashed_lines, dest=derived.hashed, unifying=10
    ):
        atomic.buf_clear_namespace(buf, ns, i1, i2)
        atomic.buf_set_lines(buf, i1, i2, True, derived.lines[j1:j2])

        for idx, highlights in enumerate(derived.highlights[j1:j2], start=i1):
            for hl in highlights:
                atomic.buf_add_highlight(buf, ns, hl.group, idx, hl.begin, hl.end)

        for idx, badges in enumerate(derived.badges[j1:j2], start=i1):
            vtxt = tuple((bdg.text, bdg.group) for bdg in badges)
            if use_extmarks:
                atomic.buf_set_extmark(
                    buf, ns, idx, -1, {"virt_text": vtxt, "hl_mode": "combine"}
                )
            else:
                atomic.buf_set_virtual_text(buf, ns, idx, vtxt, {})

    atomic.buf_set_var(buf, str(_NS), derived.hashed)
    return atomic


async def _winline(win: Window) -> Optional[int]:
    return await Nvim.fn.luaeval(NoneType, _LUA, (win,))


async def redraw(state: State, focus: Optional[PurePath]) -> None:
    focus_row = state.derived.path_row_lookup.get(focus) if focus else None

    ns = await Nvim.create_namespace(_NS)
    use_extmarks = await Nvim.api.has("nvim-0.6")

    async for win, buf in find_fm_windows():
        p_count = await buf.line_count()
        n_count = len(state.derived.lines)
        row, col = await win.get_cursor()
        (r1, c1), (r2, c2) = await operator_marks(buf, visual_type=None)
        buf_var = await buf.vars.get(NoneType, str(_NS))

        try:
            hashed_lines = _DECODER(buf_var)
        except DecodeError:
            hashed_lines = ("",)

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

        a2 = _update(
            use_extmarks,
            buf=buf,
            ns=ns,
            derived=state.derived,
            hashed_lines=hashed_lines,
        )

        a3 = Atomic()
        a3.buf_set_option(buf, "modifiable", False)
        a3.call_function("setpos", ("'<", (buf.number, r1 + 1, c1 + 1, 0)))
        a3.call_function("setpos", ("'>", (buf.number, r2 + 1, c2, 0)))
        if new_row is not None:
            if win_line := await _winline(win):
                win_height = await win.get_height()
                win_lo = win_line
                win_hi = win_line + win_height - 1
                win_p = await Nvim.fn.line(int, ".", win)
                if win_p < win_lo or win_p > win_hi:
                    lo = max(1, new_row - win_height // 2)
                    hi = min(n_count, new_row + win_height // 2)
                    a3.win_set_cursor(win, (lo, 0))
                    a3.win_set_cursor(win, (hi, 0))
            a3.win_set_cursor(win, (new_row, col))

        # a3.buf_set_name(buf, f"#{URI_SCHEME}://{state.root.path}")

        try:
            await (a1 + a2 + a3).commit(NoneType)
        except NvimError as e:
            raise UnrecoverableError(e)
