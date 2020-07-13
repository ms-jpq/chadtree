from asyncio import Queue, sleep
from typing import AsyncIterator


async def schedule(
    chan: Queue, min_time: float, max_time: float
) -> AsyncIterator[float]:
    while True:
        yield 2
        await sleep(max_time)
