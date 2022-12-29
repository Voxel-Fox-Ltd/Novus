import functools
from typing import Optional

import discord


def interaction_filter(
        *,
        start: Optional[str] = None,
        end: Optional[str] = None):
    """
    A decorator to filter out events with ``custom_id``s that don't start or
    end with a certain string when that ``custom_id`` is split by spaces.
    This check is case sensitive.

    The listener will then be called with the custom ID (split by string) as
    additional parameters.

    Although in the checks subpackage, this isn't called as a check or raises
    any exceptions. It's just a decorator to filter out events.

    .. versionadded:: 0.2.4

    Example:

    .. code-block:: python3

        @vbu.Cog.listener("on_component_interaction")
        @vbu.interaction_filter(start='foo')
        async def on_interaction(self, interaction, *args):
            '''
            This will only be called if the interaction's custom ID starts with
            `foo`.

            Passing custom IDs:
            * `foo bar` will pass
            * `foo` will pass
            * `foo bar baz` will pass
            The *args will be `['bar']`, `[]`, and `['bar', 'baz']` respectively.

            Failing custom IDs:
            * `bar foo` will fail
            * `bar foo baz` will fail
            * `bar` will fail
            * `FOO` will fail
            * `fOo` will fail
            '''

            print(*args)

    Parameters
    ----------
    start : Optional[str]
        The string the custom ID must start with.
    end : Optional[str]
        The string the custom ID must end with.
    """

    def inner(func):
        @functools.wraps(func)
        async def wrapper(*args):
            interaction: discord.Interaction = args[-1]
            if not interaction.custom_id:
                return
            custom_id_list = interaction.custom_id.split(" ")
            if start and not custom_id_list[0] == start:
                return
            elif start:
                custom_id_list.pop(0)
            if end and not custom_id_list[-1] == end:
                return
            elif end:
                custom_id_list.pop(-1)
            return await func(*args, *custom_id_list)
        return wrapper
    return inner
