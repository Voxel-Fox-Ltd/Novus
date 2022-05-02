import asyncio
from typing import Union, Callable, Optional

import discord


def component_check(
        user: Union[discord.User, discord.Member], 
        message: discord.Message, 
        no_interact_message: Optional[str] = discord.utils.MISSING) -> Callable[[discord.Interaction], bool]:
    """
    A check for a wait_for that allows only a user to interact with the given
    button, outputting the no interaction message.
    
    .. versionadded:: 0.6.6
    
    Parameters
    ----------
    user : Union[discord.User, discord.Member]
        The user who's allowed to interact with the message.
    message : discord.Message
        The message that the user is allowed to interact with.
    no_interact_message : Optional[str]
        The content that's output when a non-valid user interacts with the button.

        .. versionchanged:: 0.7.0

        You can now disable a response being sent by passing ``None`` to this parameter. If you do, a deferred
        update will still be sent.
    
    Returns
    -------
    Callable[[discord.Interaction], bool]
        A callable check for interaction events where only the supplied user is allowed to interact.
    """

    if no_interact_message == discord.utils.MISSING:
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
