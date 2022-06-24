import asyncio
from typing import Iterable, Union, Callable, Optional

import discord

from .string import Formatter


def component_check(
        user: Union[discord.User, discord.Member],
        message: discord.Message,
        no_interact_message: Optional[str] = discord.utils.MISSING) -> Callable[[discord.Interaction], bool]:
    """
    A check for a wait_for that allows only a user to interact
    with the given button, outputting the no interaction message.

    Parameters
    ----------
    user : Union[discord.User, discord.Member]
        The user who's allowed to interact with the message.
    message : discord.Message
        The message that the user is allowed to interact with.
    no_interact_message : Optional[str]
        The content that's output when a non-valid user interacts
        with the button.
        You can disable a response being sent by passing ``None``
        to this parameter. If you do, a deferred update will still be
        sent.

    Returns
    -------
    Callable[[discord.Interaction], bool]
        A callable check for interaction events where only the
        supplied user is allowed to interact.
    """

    if no_interact_message is discord.utils.MISSING:
        no_interact_message = f"Only {user.mention} can interact with this component."

    def check(payload: discord.Interaction):
        assert payload.message
        assert payload.user
        if payload.message.id != message.id:
            return False
        if payload.user.id != user.id:
            loop = asyncio.get_event_loop()
            if no_interact_message:
                loop.create_task(payload.response.send_message(
                    no_interact_message,
                    ephemeral=True,
                    allowed_mentions=discord.AllowedMentions.none(),
                ))
            else:
                loop.create_task(payload.response.defer_update())
            return False
        return True
    return check


def component_id_check(
        users: Union[discord.abc.Snowflake, Iterable[discord.abc.Snowflake]],
        custom_id: str,
        no_interact_message: Optional[str] = discord.utils.MISSING) -> Callable[[discord.Interaction], bool]:
    """
    A check for a wait_for that allows only a user to interact
    with the given button, outputting the no interaction message.

    .. versionadded:: 0.1.5

    Parameters
    ----------
    users : Union[discord.abc.Snowflake, Iterable[discord.abc.Snowflake]]
        A user or list of users who are allowed to interact with the message.
    custom_id : str
        The custom ID that we're searching for. Will be put into a
        `.startswith` for the interaction's custom ID.
    no_interact_message : Optional[str], optional
        The content that's output when a non-valid user interacts
        with the button.
        You can disable a response being sent by passing ``None``
        to this parameter. If you do, a deferred update will still be
        sent.

    Returns
    -------
    Callable[[discord.Interaction], bool]
        A callable check for interaction events where only the
        supplied user is allowed to interact.
    """

    # Set a default interaction message
    if isinstance(users, discord.abc.Snowflake):
        users = [users]
    mentions = [f"<@{user.id}>" for user in users]
    if no_interact_message is discord.utils.MISSING:
        no_interact_message = Formatter().format(
            (
                "Only {mentions:humanjoin} can interact with "
                "this message."
            ),
            mentions,
        )

    # Set up a check
    def check(payload: discord.Interaction[str]):
        assert payload.user

        # See if the custom ID is right
        if not payload.custom_id.startswith(custom_id):
            return False

        # See if the user is right
        if payload.user.id != user.id:
            loop = asyncio.get_event_loop()
            if no_interact_message:
                loop.create_task(payload.response.send_message(
                    no_interact_message,
                    ephemeral=True,
                    allowed_mentions=discord.AllowedMentions.none(),
                ))
            else:
                loop.create_task(payload.response.defer_update())
            return False  # fallback
        return True

    # And done
    return check
