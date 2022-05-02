import collections
import time
import typing

import discord
from discord.ext import commands


class CooldownMapping(commands.CooldownMapping):
    """
    A mapping of cooldowns and who's run them, so we can keep track of individuals' rate limits.
    """

    def __init__(self):
        pass

    def copy(self) -> commands.CooldownMapping:
        """
        Retuns a copy of the mapping, including a copy of its current cache.
        """

        return super().copy()

    @property
    def valid(self) -> bool:
        """
        Whether or not the mapping is valid.
        """

        return super().valid

    def _bucket_key(self, message: discord.Message) -> typing.Optional[int]:
        """
        Gets the key for the given cooldown mapping, depending on the type of the cooldown.
        """

        return super()._bucket_key(message)

    def get_bucket(self, message: discord.Message, current: float = None) -> commands.Cooldown:
        """
        Gives you the applied cooldown for a message, which you can use to work out whether to run the command or not.
        """

        return super().get_bucket(message, current)

    def update_rate_limit(self, message: discord.Message, current: float = None) -> None:
        """
        Updates the rate limit for a given message.
        """

        return super().update_rate_limit(message, current)

    def __call__(self, original: commands.Cooldown):
        """
        :meta private:

        Runs the original init method.

        Args:
            original (commands.Cooldown): The original cooldown that this mapping refers to.
        """

        self._cooldown = original
        self._cooldown.mapping = self
        self._cache = {}
        return self


grouped_cooldown_mapping_cache = collections.defaultdict(dict)


class GroupedCooldownMapping(CooldownMapping):
    """
    A grouped cooldown mapping class so that you can easily apply a single cooldown to multiple
    commands.

    Examples:

        ::

            @voxelbotutils.command()
            @voxelbotutils.cooldown.cooldown(
                1, 60, commands.BucketType.user,
                mapping=voxelbotutils.cooldown.GroupedCooldownMapping("group"))
            async def commandone(self, ctx):
                '''These two commands will be subject to the same cooldown.'''

            @voxelbotutils.command()
            @voxelbotutils.cooldown.cooldown(
                1, 60, commands.BucketType.user,
                mapping=voxelbotutils.cooldown.GroupedCooldownMapping("group"))
            async def commandtwo(self, ctx):
                '''These two commands will be subject to the same cooldown.'''
    """

    grouped_cache = grouped_cooldown_mapping_cache

    def __init__(self, key: str):
        """
        Args:
            key (str): The cooldown key that the commands will be grouped under.
        """
        self.group_cache_key = key

    @property
    def _cache(self):
        return grouped_cooldown_mapping_cache[self.group_cache_key]

    @_cache.setter
    def _cache(self, value):
        grouped_cooldown_mapping_cache[self.group_cache_key] = value


class Cooldown(commands.Cooldown):
    """
    A class handling the cooldown for an individual user. This is provided as a subclass of
    :class:`discord.ext.commands.Cooldown` and provides a :func:`predicate` function that you can use
    to change aspects of a given command's cooldown
    """

    default_cooldown_error = commands.CommandOnCooldown
    default_mapping_class = CooldownMapping

    _copy_kwargs = ()  # The attrs that are passed into kwargs when copied; error and mapping are always copied
    __slots__ = ('rate', 'per', 'type', 'error', 'mapping', '_window', '_tokens', '_last')

    def __init__(self, *, error: commands.CommandOnCooldown = None, mapping: CooldownMapping = None):
        """
        Args:
            error (None, optional): The error instance to be raised if the user is on cooldown.
            mapping (CooldownMapping, optional): The cooldown mapping to be used.
        """

        self.error = error
        self.mapping = mapping

    def predicate(self, ctx) -> bool:
        """
        A function that runs before each command call, so you're able to update anything
        before the command runs. Most likely you'll be using this to update the self.per attr so that
        cooldowns can be tailored to the individual. Everything this method returns is discarded.
        This method CAN be a coroutine.
        """

        return True

    def get_tokens(self, current: float = None) -> int:
        """Gets the number of command calls that can still be made before hitting the rate limit

        Args:
            current (float, optional): The current time, or now (via `time.time()`). Is _not_ used to update self._last,
                since the command may not have actually been called.

        Returns:
            int: The number of times this command has been used given the time limit.
        """

        return super().get_tokens(current)

    def update_rate_limit(self, current: float = None) -> typing.Optional[int]:
        """
        Updates the rate limit for the command, as it has now been called.

        Args:
            current (float, optional): The current time, or now (via `time.time()`).
        """

        return super().update_rate_limit(current)

    def get_remaining_cooldown(self, current: float = None) -> typing.Optional[float]:
        """
        Gets the remaining rate limit for the command.
        """

        current = current or time.time()
        if self.get_tokens() == 0:
            return self.per - (current - self._window)
        return None

    def reset(self) -> None:
        """
        Resets the cooldown for the given command.
        """

        return super().reset()

    def copy(self) -> commands.Cooldown:
        """
        Returns a copy of the cooldown.
        """

        kwargs = {attr: getattr(getattr(self, attr, None), 'copy', lambda: attr)() for attr in self._copy_kwargs}
        cooldown = self.__class__(error=self.error, mapping=self.mapping, **kwargs)
        cooldown = cooldown(rate=self.rate, per=self.per, type=self.type)
        return cooldown

    def __call__(self, rate: float, per: int, type: commands.BucketType) -> 'Cooldown':
        """
        Runs the original init method. MUST return self.

        Args:
            rate (float): How many times the command can be called (rate) in a given amount of time (per) before being applied.
            per (int): How many times the command can be called (rate) in a given amount of time (per) before being applied.
            type (commands.BucketType): How the cooldown should be applied.

        Returns:
            Cooldown: The cooldown object.
        """

        try:
            if self.type:
                type = self.type
        except AttributeError:
            pass
        super().__init__(rate, per, type)
        return self


class NoRaiseCommandOnCooldown(commands.CommandOnCooldown):
    """A version of :class:`discord.ext.commands.CommandOnCooldown` that doesn't output an error."""


class NoRaiseCooldown(Cooldown):
    """
    A version of :class:`Cooldown` that doesn't raise an error if the
    cooldown fails.
    """

    default_cooldown_error = NoRaiseCommandOnCooldown


def cooldown(
        rate: int, per: int, type: commands.BucketType = commands.BucketType.default, *,
        cls: commands.Cooldown = None) -> typing.Callable:
    """
    Args:
        rate (int): How many times this command can be run.
        per (int): The time before which the cooldown for this command is reset.
        type (commands.BucketType, optional): The bucket that the cooldown should be applied for.
        cls (commands.Cooldown, optional): The cooldown class instance.

    Returns:
        typing.Callable: The decorator that should be applied to the command.
    """

    if cls is None:
        cls = Cooldown()

    def decorator(func):
        if isinstance(func, commands.Command):
            mapping = cls.mapping or cls.default_mapping_class()
            func._buckets = mapping(cls(rate, per, type))
        else:
            func.__commands_cooldown__ = cls(rate, per, type)
        return func
    return decorator


def no_raise_cooldown(*args, **kwargs):
    cls = kwargs.pop('cls', NoRaiseCooldown())
    return cooldown(*args, cls=cls, **kwargs)
