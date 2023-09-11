"""
Copyright (c) Kae Bartlett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
    from .plugin import Plugin

__all__ = (
    'LoopBehavior',
    'loop',
    'Loop',
)

log = logging.getLogger("novus.ext.client.loop")


class LoopBehavior(Enum):
    """
    How a loop should behave on its ending.

    Attributes
    ----------
    end
        The previous loop should have finished executing before a new loop is
        triggered to start.
    immediate
        A new loop should be triggered immediately after the previous one is
        triggered.
    """

    end = auto()
    immediate = auto()


def loop(
        loop_time: float,
        end_behavior: LoopBehavior = LoopBehavior.end,
        autostart: bool = True,
        wait_until_ready: bool = True) -> Callable[..., Loop]:
    """
    A wrapper to create a loop object.

    Parameters
    ----------
    loop_time : float
        The number of seconds between each loop.
        This is not guarenteed to be accurate, but is used internally for the
        wait function.
    end_behavior: LoopBehavior
        How the loop should behave on its end.
    autostart: bool
        Whether the loop should start immediately when the plugin is loaded.
    wait_until_ready: bool
        If the plugin should wait until the bot has received the ready payload
        before beginning its task.

    Examples
    --------

    .. code-block::

        @client.loop(60)
        async def every_minute(self):
            self.log.info("Ping")
    """

    @functools.wraps(loop)
    def wrapper(func: Callable[[], Coroutine[None, None, Any]]) -> Loop:
        return Loop(
            func,
            loop_time,
            end_behavior,
            autostart,
            wait_until_ready,
        )
    return wrapper


class Loop:
    """
    A piece of code that should be looped within a plugin.

    Attributes
    ----------
    func : Callable[..., Awaitable[Any]]
        The function that is part of the loop.
    loop_time : float
        The number of seconds between each loop iteration.
    end_behavior : novus.ext.client.LoopBehaviour
        The behaviour for how each loop will end.
    autostart : bool
        If the plugin should start automatically.
    wait_until_ready : bool
        If the loop should wait until the bot receives the ready payload.
    owner : novus.ext.client.Plugin
        The plugin where the loop resides.
    task : asyncio.Task | None
        The last instance of the given function that the bot ran in this loop.
    """

    __slots__ = (
        'func',
        'loop_time',
        'end_behavior',
        'autostart',
        'wait_until_ready',
        'owner',
        'bg_task',
        'task',
        '_before',
        '_args',
        '_kwargs',
    )

    def __init__(
            self,
            func: Callable[[], Coroutine[None, None, Any]],
            loop_time: float,
            end_behavior: LoopBehavior = LoopBehavior.end,
            autostart: bool = True,
            wait_until_ready: bool = True):
        self.func = func
        self.loop_time = loop_time
        self.end_behavior = end_behavior
        self.autostart = autostart
        self.wait_until_ready = wait_until_ready
        self.owner: Plugin
        self.bg_task: asyncio.Task | None = None
        self.task: asyncio.Task | None = None
        self._before: Callable[[], Coroutine[None, None, Any]] | None = None
        self._args, self._kwargs = (), {}

    def before(self, func: Callable[[], Coroutine[None, None, Any]]) -> None:
        """
        Set a function that is to run before the loop starts.
        """

        self._before = func

    def start(self, *args, **kwargs) -> None:
        """
        Start the loop.
        """

        if self.task is not None:
            raise RuntimeError("Loop is already running!")
        log.info("Starting in background Loop[%s.%s]", self.owner.__name__, self.func.__name__)
        self._args = args
        self._kwargs = kwargs
        self.bg_task = asyncio.create_task(self._run(), name=f"Loop[{self.owner.__name__}.{self.func.__name__}()]")

    async def _run(self) -> None:
        if self.wait_until_ready:
            await self.owner.bot.wait_until_ready()
        if self._before:
            await self._before()
        while True:
            try:
                await asyncio.sleep(self.loop_time)
            except asyncio.CancelledError:
                return
            log.info("Running Loop[%s.%s()]", self.owner.__name__, self.func.__name__)
            task = asyncio.create_task(self.func(self.owner, *self._args, **self._kwargs))  # pyright: ignore
            if self.end_behavior == LoopBehavior.end:
                await asyncio.wait([task])

    def __call__(self, *args, **kwargs):
        return self.func(self.owner, *args, **kwargs)  # pyright: ignore

    def stop(self) -> None:
        """
        Stop the loop. This will not stop the currently running task instance,
        if one is running.

        .. seealso:: :meth:`novus.ext.client.Loop.cancel`
        """

        if self.bg_task is None:
            return
        self.bg_task.cancel()

    def cancel(self) -> None:
        """
        Stop the loop and cancel any running tasks.

        .. seealso:: :meth:`novus.ext.client.Loop.stop`
        """

        self.stop()
        if self.task is None:
            return
        self.task.cancel()

