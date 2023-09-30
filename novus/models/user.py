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

import functools
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from typing_extensions import Self

from ..enums import Locale, UserPremiumType
from ..flags import UserFlags
from ..utils import cached_slot_property, generate_repr, try_enum, try_snowflake
from .abc import Hashable, Messageable
from .asset import Asset

if TYPE_CHECKING:
    from .. import abc, payloads
    from ..api import HTTPConnection
    from . import Channel, GuildMember, OauthGuild

__all__ = (
    'User',
)


class User(Hashable, Messageable):
    """
    A model for a user object.

    Attributes
    ----------
    id : int
        The ID of the user.
    username : str
        The username of the user.
    discriminator : str
        The discriminator of the user.
    avatar_hash : str | None
        The avatar hash of the user.
    avatar : novus.Asset | None
        The avatar of the user.
    bot : bool
        Whether or not the user is associated with an Oauth2 application.
    system : bool
        Whether or not the user is associated with a Discord system message.
    mfa_enabled : bool
        Whether or not there's MFA available on the account. Only set properly
        for when you're receiving your own user via an Oauth2 application.
    banner_hash : str | None
        The hash for the user banner.
    banner : novus.Asset | None
        The asset for the user banner.
    accent_color : int
        The color associated with the user's accent color.
    locale : novus.Locale | None
        The locale for the user. Only set properly for when you're receiving
        your own user via an Oauth2 application.
    verified : bool
        Whether or not the user has a verified username attached. Only set
        properly for when you're receiving your own user via an Oauth2
        application.
    email : str | None
        The email associated with the account. Only set properly for when
        you're receiving your own user via an Oauth2 application.
    flags : novus.UserFlags
        The flags associated with the user account. A combination of public and
        private.
    premium_type : novus.UserPremiumType
        The premium type associated with the account.
    """

    __slots__ = (
        'state',
        'id',
        'username',
        'discriminator',
        'avatar_hash',
        'bot',
        'system',
        'mfa_enabled',
        'banner_hash',
        'accent_color',
        'locale',
        'verified',
        'email',
        'flags',
        'premium_type',
        '_cs_avatar',
        '_cs_default_avatar',
        '_cs_banner',
        '_guilds',
        '_dm_channel',
    )

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.User | payloads.PartialUser):
        self.state = state
        self.id = try_snowflake(data['id'])
        self._guilds: set[int] = set()
        self._dm_channel: Channel | None = None
        self._update(data)

    __repr__ = generate_repr(('id', 'username', 'bot',))

    def __str__(self) -> str:
        if self.discriminator == "0":
            return self.username
        return f"{self.username}#{self.discriminator}"

    @property
    def mention(self) -> str:
        """
        A ping for the user.
        """

        return f"<@{self.id}>"

    @cached_slot_property('_cs_avatar')
    def avatar(self) -> Asset | None:
        if self.avatar_hash is None:
            return None
        return Asset.from_user_avatar(self)

    @cached_slot_property('_cs_default_avatar')
    def default_avatar(self) -> Asset:
        return Asset.from_default_user_avatar(self)

    @property
    def display_avatar(self) -> Asset:
        return self.avatar or self.default_avatar

    @cached_slot_property('_cs_banner')
    def banner(self) -> Asset | None:
        if self.banner_hash is None:
            return None
        return Asset.from_user_banner(self)

    def _upgrade(self, data: payloads.GuildMember) -> GuildMember:
        """
        Upgrade a user member to a guild member if we can. Adds to guild cache.
        """

        from .guild_member import GuildMember
        v = GuildMember(
            state=self.state,
            data=data,
            user=self,
        )
        self._guilds.add(v.guild.id)
        return v

    def _update(self, data: payloads.User | payloads.PartialUser) -> Self:
        """
        Update the user instance if we get any new data from the API.
        """

        self.username = data['username']
        self.discriminator = data['discriminator']
        del self.default_avatar
        self.avatar_hash = data.get('avatar')
        del self.avatar
        self.bot = data.get('bot', False)
        self.system = data.get('system', False)
        self.mfa_enabled = data.get('mfa_enabled', False)
        self.banner_hash = data.get('banner')
        del self.banner
        self.accent_color = data.get('accent_color')
        self.locale = try_enum(Locale, data.get('locale'))
        self.verified = data.get('verified', False)
        self.email = data.get('email')
        self.flags = UserFlags(0)
        if 'flags' in data or 'public_flags' in data:
            self.flags = UserFlags(
                data.get('flags', 0) | data.get('public_flags', 0)
            )
        self.premium_type = try_enum(UserPremiumType, data.get('premium_type', 0))
        return self

    # API methods

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            id: int) -> User:
        """
        Get an instance of a user from the API.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        id : int
            The ID associated with the user you want to get.

        Returns
        -------
        novus.User
            The user associated with the given ID.
        """

        return await state.user.get_user(id)

    @classmethod
    async def fetch_me(
            cls,
            state: HTTPConnection) -> User:
        """
        Get the user associated with the current connection.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.

        Returns
        -------
        novus.User
            The user associated with the given ID.
        """

        return await state.user.get_current_user()

    @classmethod
    async def fetch_my_guilds(
            cls,
            state: HTTPConnection,
            *,
            before: int | None = None,
            after: int | None = None,
            limit: int = 200) -> list[OauthGuild]:
        """
        Return a list of partial guild objects that the current user is a
        member of.

        The endpoint returns 200 guilds by default, which is the maximum number
        of guilds that a non-bot can join.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        before: int | None
            The snowflake before which to get guilds.
        after: int | None
            The snowflake after which to get guilds.
        limit: int
            The number of guilds you want to return.

        Returns
        -------
        list[novus.OauthGuild]
            A list of guilds associated with the current user.
        """

        return await state.user.get_current_user_guilds(
            before=before,
            after=after,
            limit=limit,
        )

    async def create_dm_channel(
            self: abc.StateSnowflake) -> Channel:
        """
        Open a DM channel with the given user.

        Returns
        -------
        novus.Channel
            The DM channel for the user.
        """

        return await self.state.user.create_dm(self.id)

    async def _get_send_method(self) -> Callable[..., Awaitable[Any]]:
        """
        Return a snowflake implementation with the ID of the channel, and the
        sendable method.
        """

        if self._dm_channel is None:
            self._dm_channel = await self.create_dm_channel()
        return functools.partial(self.state.channel.create_message, self._dm_channel.id)
