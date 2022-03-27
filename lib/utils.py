import asyncio

__all__ = [
    "schedule"
]

def schedule(callable_or_coroutine, *Args, **Kwargs):
    func = callable_or_coroutine
    if not asyncio.iscoroutine(func):
        async def inner():
            return func(*Args, **Kwargs)
        return asyncio.create_task(inner())
    else:
        return asyncio.create_task(func(*Args, **Kwargs))
