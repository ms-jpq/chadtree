from .da import tiktok


async def tasks() -> None:
    async for _ in tiktok(1):
        pass
