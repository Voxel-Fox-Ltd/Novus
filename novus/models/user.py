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
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from typing_extensions import Self

from ..enums import Status
from ..flags import UserFlags
from ..utils import DiscordDatetime, cached_slot_property, generate_repr, try_snowflake
from .abc import Hashable, Messageable
from .asset import Asset

if TYPE_CHECKING:
    from .. import abc, payloads
    from ..api import HTTPConnection
    from . import Channel, GuildMember, OauthGuild

__all__ = (
    "User",
    "UserActivity",
    "Collectibles",
    "Nameplate",
    "PrimaryGuild",
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
    global_name : str | None
        The global name of the user.
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
    locale : str | None
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
    premium_type : int
        The premium type associated with the account.

        .. seealso:: `novus.UserPremiumType`
    status : str
        The status of the user.

        .. seealso:: `novus.Status`
    activities : list[novus.Activity]
        The activites of the user.
    collectibles : novus.Collectibles
        The collectibles that the user has.
    primary_guild : novus.PrimaryGuild | None
        The primary guild of the user. Shown as a guild tag on the user's profile.
    """

    __slots__ = (
        "state",
        "id",
        "username",
        "global_name",
        "discriminator",
        "avatar_hash",
        "bot",
        "system",
        "mfa_enabled",
        "banner_hash",
        "accent_color",
        "locale",
        "verified",
        "voice",
        "email",
        "flags",
        "premium_type",
        "status",
        "activites",
        "collectibles",
        "primary_guild",
        "_cs_avatar",
        "_cs_default_avatar",
        "_cs_banner",
        "_guilds",
        "_dm_channel",
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

    __repr__ = generate_repr(('id', 'global_name', 'bot',))

    def __str__(self) -> str:
        if self.discriminator == "0":
            return self.global_name or self.username
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
        self.global_name = data.get('global_name')
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
        self.locale = data.get('locale')
        self.verified = data.get('verified', False)
        self.email = data.get('email')
        self.flags = UserFlags(0)
        if 'flags' in data or 'public_flags' in data:
            self.flags = UserFlags(
                data.get('flags', 0) | data.get('public_flags', 0)
            )
        self.premium_type = data.get('premium_type', 0)
        self.status = Status.ONLINE
        self.activites: list[UserActivity] = []
        self.collectibles = Collectibles(data.get("collectibles") or {})
        self.primary_guild = data.get("primary_guild")

        return self

    def _update_presence(self, data: payloads.Presence) -> Self:
        """
        Update the presence for this user.
        """

        self.status = data.get("status") or Status.ONLINE
        self.activites = [
            UserActivity(data=d)
            for d in data.get("activities", [])
        ]
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


class UserActivity:
    """
    A user activity for their presence.
    """

    def __init__(self, *, data: payloads.Activity):
        self.name = data["name"]
        self.type = data["type"]
        self.created_at = DiscordDatetime.fromtimestamp(data["created_at"] / 1_000)


class Collectibles:
    """
    A collection of the collectibles that a user has.

    Attributes
    ----------
    nameplate : novus.Nameplate | None
        The user's nameplate.
    """

    __slots__ = (
        "nameplate",
    )

    def __init__(self, data: payloads.Collectibles):
        self.nameplate = None
        if "nameplate" in data:
            try:
                self.nameplate = Nameplate(data["nameplate"])
            except Exception:
                # Somehow Discord has given us an invalid nameplate object
                logging.getLogger("novus.models.user").warning(
                    "Failed to parse user nameplate data: %s",
                    data["nameplate"],
                )


class Nameplate:
    """
    A nameplate decoration for a user.

    Attributes
    ----------
    sku_id: int
        The SKU ID associated with the nameplate.
    asset_hash: str
        The asset hash associated with the nameplate.
    asset : novus.Asset
        The asset associated with the nameplate.
    label: str
        The label associated with the nameplate.
    palette: str
        The palette associated with the nameplate.
    """

    __slots__ = (
        "sku_id",
        "asset_hash",
        "label",
        "palette",
        "_cs_asset",
    )

    def __init__(self, data: payloads.Nameplate):
        self.sku_id = try_snowflake(data["sku_id"])
        self.asset_hash = data["asset"]
        self.label = data["label"]
        self.palette = data["palette"]
        self._cs_asset: Asset | None = None

    @cached_slot_property("_cs_asset")
    def asset(self) -> Asset | None:
        if self.asset_hash is None:
            return None
        return Asset.from_nameplate(self)


class PrimaryGuild:
    """
    The primary guild for a user.

    Attributes
    ----------
    identity_guild_id: int
        The ID of the primary guild.
    identity_enabled: bool
        Whether or not the user's primary guild is enabled.
    tag: str
        The tag associated with the primary guild.
    badge_hash: str
        The hash associated with the primary guild badge.
    badge: novus.Asset
        The asset associated with the primary guild badge.
    """

    __slots__ = (
        "identity_guild_id",
        "identity_enabled",
        "tag",
        "badge_hash",
        "_cs_badge",
    )

    def __init__(self, data: payloads.PrimaryGuild):
        self.identity_guild_id = try_snowflake(data["identity_guild_id"])
        self.identity_enabled = data["identity_enabled"]
        self.tag = data["tag"]
        self.badge_hash = data["badge"]

    @cached_slot_property("_cs_badge")
    def badge(self) -> Asset | None:
        return Asset.from_primary_guild(self)
