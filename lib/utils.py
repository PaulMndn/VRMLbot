import asyncio
from typing import Callable, Coroutine, Any
from collections.abc import Awaitable

__all__ = [
    "schedule"
]

def schedule(callable_or_coroutine: Callable[..., Any] | Coroutine[Any, Any, Any], *Args, **Kwargs) -> asyncio.Task[Any]:
    func = callable_or_coroutine
    if not asyncio.iscoroutine(func):
        async def inner() -> Any:
            return func(*Args, **Kwargs)
        return asyncio.create_task(inner())
    else:
        return asyncio.create_task(func(*Args, **Kwargs))
