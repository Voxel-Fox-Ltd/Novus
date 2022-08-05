import inspect
from typing import Awaitable, Callable

from discord.ext.commands import converter as converters


def async_wrap_callback(callback) -> Callable[..., Awaitable]:
    """
    Wraps a function in an async function.
    """

    if inspect.isawaitable(callback) or inspect.iscoroutine(callback) or inspect.iscoroutinefunction(callback):
        return callback

    async def wrapper(*args, **kwargs):
        if callback is None:
            return None
        return callback(*args, **kwargs)
    return wrapper


def get_discord_converter(cls):
    """
    Get a Discord converter instance from a normal Discord model.
    """

    try:
        module = cls.__module__
    except AttributeError:
        pass
    else:
        if module is not None and (module.startswith('discord.') and not module.endswith('converter')):
            cls = getattr(converters, cls.__name__ + 'Converter', cls)
    return cls
