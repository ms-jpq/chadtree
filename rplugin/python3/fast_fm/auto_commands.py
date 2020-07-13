from asyncio import Queue

from .commands import redraw
from .consts import throttle_duration
from .da import async_throttle
from .git import status
from .keymap import keymap
from .nvim import Nvim2, find_buffer
from .state import forward
from .types import Settings, State
from .wm import is_fm_buffer


@async_throttle(delay_seconds=throttle_duration)
async def _refresh(chan: Queue, nvim: Nvim2, state: State, settings: Settings) -> None:
    vc = await status()
    new_state = await forward(state, settings=settings, vc=vc)
    await redraw(nvim, state=new_state)
    await chan.put(new_state)


async def a_on_filetype(
    nvim: Nvim2, state: State, settings: Settings, buf: int
) -> None:
    buffer = await find_buffer(nvim, buf)
    if buffer is not None:
        await keymap(nvim, buffer=buffer, settings=settings)


async def a_on_bufenter(
    chan: Queue, nvim: Nvim2, state: State, settings: Settings, buf: int
) -> None:
    buffer = await find_buffer(nvim, buf)
    if buffer is not None and await is_fm_buffer(nvim, buffer=buffer):
        await _refresh(chan, nvim, state=state, settings=settings)


async def a_on_focus(
    chan: Queue, nvim: Nvim2, state: State, settings: Settings
) -> None:
    return await _refresh(chan, nvim, state=state, settings=settings)
