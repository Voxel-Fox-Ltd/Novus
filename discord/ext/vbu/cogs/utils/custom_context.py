from typing import TypeVar, Optional, Generic, Union
import collections

import discord
from discord.ext import commands


GuildT = TypeVar("GuildT", None, discord.Guild, Optional[discord.Guild])


FakeResponse = collections.namedtuple("FakeResponse", ["status", "reason"])


class AbstractMentionable(discord.Object):
    """
    A fake mentionable object for use anywhere that you can't catch an error on a ``.mention`` being ``None``.

    Attributes:
        id (int): The ID of the mentionable.
        mention (str): The mention string for the object.
        name (str): The name of the object.
    """

    def __init__(self, id: int, mention: str = "null", name: str = "null"):
        """
        Args:
            id (int): The ID of the mentionable.
            mention (str): The string to be returned when ``.mention`` is run.
            name (str): The string to be returned when ``.name`` is run.
        """

        self.id = id
        self.mention = mention
        self.name = name

    def __str__(self):
        return self.name


class ContextMixin:

    guild: Optional[discord.Guild]

    def get_mentionable_channel(self, channel_id: int, fallback: str = "null") -> Union[discord.TextChannel, AbstractMentionable]:
        """
        Get the mention string for a given channel ID.

        Args:
            channel_id (int): The ID of the channel that you want to mention.
            fallback (str, optional): The string to fall back to if the channel isn't reachable.

        Returns:
            Union[discord.TextChannel, voxelbotutils.AbstractMentionable]: The mentionable channel.
        """

        x = None
        if channel_id is not None and self.guild:
            x = self.guild.get_channel(int(channel_id))
        if x:
            return x
        return AbstractMentionable(channel_id, fallback, fallback)

    def get_mentionable_role(self, role_id: int, fallback: str = "null") -> Union[discord.Role, AbstractMentionable]:
        """
        Get the mention string for a given role ID.

        Args:
            role_id (int): The ID of the role that you want to mention.
            fallback (str, optional): The string to fall back to if the role isn't reachable.

        Returns:
            Union[discord.Role, voxelbotutils.AbstractMentionable]: The mentionable role.
        """

        x = None
        if role_id is not None and self.guild:
            x = self.guild.get_role(int(role_id))
        if x:
            return x
        return AbstractMentionable(role_id, fallback, fallback)


class Context(commands.Context, ContextMixin, Generic[GuildT]):
    """
    A modified version of the default :class:`discord.ext.commands.Context`.

    Attributes:
        original_author_id (int): The ID of the original person to run the command. Persists through
            the bot's ``sudo`` command, if you want to check the original author.
    """

    guild: GuildT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_author_id: Optional[int]
        try:
            self.original_author_id = self.author.id
        except AttributeError:
            self.original_author_id = None

    async def okay(self) -> None:
        """
        Adds the okay hand reaction to a message.
        """

        return await self.message.add_reaction("\N{OK HAND SIGN}")


class SlashContext(commands.SlashContext, ContextMixin, Generic[GuildT]):

    guild: GuildT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_author_id: Optional[int]
        try:
            self.original_author_id = self.author.id
        except AttributeError:
            self.original_author_id = None

    async def okay(self) -> None:
        """
        Sends an okay hand emoji.
        """

        await self.send("\N{THUMBS UP SIGN}")


class _NoRequestTyping(object):

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        pass


class _FakeStateMessage(discord.Message):

    def __init__(self, state):
        self._state = state


class PrintContext(Context):

    def __init__(self, bot):
        self.message = _FakeStateMessage(bot._connection)
        self.bot = bot
        self.prefix = ">>> "

    async def send(self, content, *args, **kwargs):
        print(content, args, kwargs)
        if (file := kwargs.get("file", None)):
            if isinstance(file.fp, str):
                pass
            else:
                loc = file.fp.tell()
                print(file.fp.read())
                file.fp.seek(loc)

    async def trigger_typing(self):
        pass

    def typing(self):
        return _NoRequestTyping()
