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

import operator
from typing import TYPE_CHECKING, Any, Awaitable, Callable
from typing_extensions import Self

from ..flags import Permissions, UserFlags
from ..utils.cached_slots import cached_slot_property
from ..utils.missing import MISSING
from ..utils.repr import generate_repr
from ..utils.snowflakes import try_id, try_object, try_snowflake
from ..utils.times import parse_timestamp
from .abc import Hashable, Messageable
from .asset import Asset
from .channel import DMChannel
from .user import User

if TYPE_CHECKING:
    from datetime import datetime as dt

    from .. import abc, enums, payloads
    from ..api import HTTPConnection
    from .guild import BaseGuild
    from .voice_state import VoiceState

__all__ = (
    'GuildMember',
    'ThreadMember',
)


class GuildMember(Hashable, Messageable):
    """
    A model for a guild member object.

    This model does not extend the `novus.User` object, but but has the same
    methods and attributes.

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
    nick : str | None
        The nickname for the user.
    guild_avatar_hash : str | None
        The guild avatar hash for the user.
    guild_avatar : novus.Asset | None
        The guild avatar for the user.
    role_ids : list[int]
        A list of role IDs that the user has.
    joined_at : datetime.datetime
        When the user joined the guild.
    premium_since : datetime.datetime | None
        When the user started boosting the guild.
    deaf : bool
        If the user is deafened in voice channels.
    mute : bool
        If the user is muted in voice channels.
    pending : bool
        If the user has not yet passed membership screening.
    permissions : novus.Permissions | None
        The total permissions for the user in the channel, including overwrites.
        Only returned within an interaction.
    timeout_until : datetime.datetime | None
        When the user's timeout will expire and the user will be able to
        communicate again.
    guild : novus.abc.StateSnowflake | novus.Guild | None
        The guild that the member is part of. May be ``None`` in some rare
        cases (such as when getting raw API requests).
    voice : novus.VoiceState | None
        The user's voice state.
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
        '_cs_banner',

        '_user',
        'nick',
        'guild_avatar_hash',
        'role_ids',
        'joined_at',
        'premium_since',
        'deaf',
        'mute',
        'pending',
        'permissions',
        'timeout_until',
        'guild',
        '_cs_guild_avatar',
    )

    # User
    id: int
    username: str
    discriminator: str
    avatar_hash: str | None
    bot: bool
    system: bool
    mfa_enabled: bool
    banner_hash: str | None
    accent_color: int | None
    locale: enums.Locale | None
    verified: bool
    email: str | None
    flags: UserFlags
    premium_type: enums.UserPremiumType

    # Member
    nick: str | None
    guild_avatar_hash: str | None
    role_ids: list[int]
    joined_at: dt
    premium_since: dt | None
    deaf: bool
    mute: bool
    pending: bool
    permissions: Permissions
    timeout_until: dt | None
    guild: BaseGuild

    def __new__(cls, **kwargs: Any) -> GuildMember:
        obj = super().__new__(cls)
        for attr in User.__slots__:
            if attr.startswith("_") or attr == "state":
                continue
            getter = operator.attrgetter('_user.' + attr)
            setattr(
                cls,
                attr,
                property(getter, doc=f'Equivalent to :attr:`novus.User.{attr}`')
            )
        return obj

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.GuildMember,
            user: payloads.User | payloads.PartialUser | User | None = None,
            guild_id: int | str | None = None):
        self.state = state
        self._user: User
        if isinstance(user, User):
            user_object = user
        else:
            if user is None:
                user = data["user"]
            user_object = self.state.cache.get_user(user["id"])
            if user_object is None:
                user_object = User(state=state, data=user)
        self._user = user_object
        self.nick = data.get("nick")
        self.guild_avatar_hash = data.get("avatar")
        self.role_ids = try_snowflake(data["roles"])
        self.joined_at = parse_timestamp(data["joined_at"])
        self.premium_since = parse_timestamp(data.get("premium_since"))
        self.deaf = data.get('deaf', False)
        self.mute = data.get('mute', False)
        self.pending = data.get('pending', False)
        self.permissions = Permissions.none()
        if "permissions" in data:
            self.permissions = Permissions(int(data["permissions"]))
        self.timeout_until = None
        if "communication_disabled_until" in data:
            self.timeout_until = parse_timestamp(data["communication_disabled_until"])
        if "guild_id" in data and guild_id is None:
            guild_id = data["guild_id"]
        if guild_id is None:
            raise ValueError("Missing guild from member init")
        self.guild = self.state.cache.get_guild(guild_id)
        self._user._guilds.add(self.guild.id)

    __repr__ = generate_repr(("id", "username", "bot", "guild",))

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

    @property
    def voice(self) -> VoiceState | None:
        from .guild import Guild
        if not isinstance(self.guild, Guild):
            return None
        return self.guild._voice_states.get(self.id)

    @cached_slot_property('_cs_avatar')
    def avatar(self) -> Asset | None:
        if self.avatar_hash is None:
            return None
        return Asset.from_user_avatar(self)

    @cached_slot_property('_cs_banner')
    def banner(self) -> Asset | None:
        if self.banner_hash is None:
            return None
        return Asset.from_user_banner(self)

    @cached_slot_property('_cs_guild_avatar')
    def guild_avatar(self) -> Asset | None:
        if self.guild_avatar_hash is None:
            return None
        return Asset.from_guild_member_avatar(self)

    def _update(self, data: payloads.GuildMember) -> Self:
        self._user._update(data["user"])
        self.nick = data.get("nick")
        self.guild_avatar_hash = data.get("guild_avatar_hash")
        self.role_ids = try_snowflake(data["roles"])
        self.joined_at = parse_timestamp(data["joined_at"])
        self.premium_since = parse_timestamp(data.get("premium_since"))
        self.deaf = data["deaf"]
        self.mute = data["mute"]
        if "pending" in data:
            self.pending = data["pending"]
        self.timeout_until = parse_timestamp(data.get("communication_disabled_until"))
        return self

    # API methods

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            guild_id: int,
            member_id: int) -> GuildMember:
        """
        Get an instance of a user from the API.

        .. seealso:: :func:`novus.Guild.fetch_member`

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the guild you want to get.
        member_id : int
            The ID associated with the user you want to get.

        Returns
        -------
        novus.GuildMember
            The user associated with the given ID.
        """

        return await state.guild.get_guild_member(guild_id, member_id)

    @classmethod
    async def fetch_me(
            cls,
            state: HTTPConnection,
            guild_id: int) -> GuildMember:
        """
        Get the member object associated with the current connection and a
        given guild ID.

        .. note:: Only usable via Oauth with the ``guilds.members.read`` scope.

        .. seealso:: :func:`novus.Guild.fetch_me`

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the guild you want to get.

        Returns
        -------
        novus.GuildMember
            The member within the given guild.
        """

        return await state.user.get_current_user_guild_member(guild_id)

    async def edit(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            nick: str | None = MISSING,
            roles: list[int | abc.Snowflake] = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING,
            voice_channel: int | abc.Snowflake | None = MISSING,
            timeout_until: dt | None = MISSING) -> GuildMember:
        """
        Edit a guild member.

        .. seealso:: :func:`novus.Guild.edit_member`

        Parameters
        ----------
        nick : str | None
            The nickname you want to set for the user.
        roles : list[novus.abc.Snowflake]
            A list of roles that you want the user to have.
        mute : bool
            Whether or not the user is muted in voice channels. Will error if
            the user is not currently in a voice channel.
        deaf : bool
            Whether or not the user is deafened in voice channels. Will error
            if the user is not currently in a voice channel.
        voice_channel : novus.abc.Snowflake | None
            The voice channel that the user is in.
        timeout_until : datetime.datetime | None
            When the user's timeout should expire (up to 28 days in the
            future).
        """

        update: dict[str, Any] = {}

        if nick is not MISSING:
            update["nick"] = nick
        if roles is not MISSING:
            update["roles"] = [try_object(r) for r in roles]
        if mute is not MISSING:
            update["mute"] = mute
        if deaf is not MISSING:
            update["deaf"] = deaf
        if voice_channel is not MISSING:
            update["channel"] = try_object(voice_channel)
        if timeout_until is not MISSING:
            update["communication_disabled_until"] = timeout_until

        return await self.state.guild.modify_guild_member(
            self.guild.id,
            self.id,
            reason=reason,
            **update,
        )

    async def add_role(
            self: abc.StateSnowflakeWithGuild,
            role: int | abc.Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Add a role to the user.

        Requires the ``MANAGE_ROLES`` permission.

        .. seealso:: :func:`novus.Guild.add_member_role`

        Parameters
        ----------
        role : int | novus.abc.Snowflake
            The role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.guild.add_guild_member_role(
            self.guild.id,
            self.id,
            try_id(role),
            reason=reason,
        )

    async def remove_role(
            self: abc.StateSnowflakeWithGuild,
            role: int | abc.Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Remove a role from the user.

        Requires the ``MANAGE_ROLES`` permission.

        .. seealso:: :func:`novus.Guild.remove_member_role`

        Parameters
        ----------
        role : int | novus.abc.Snowflake
            The role you want to remove.
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.guild.remove_guild_member_role(
            self.guild.id,
            self.id,
            try_id(role),
            reason=reason,
        )

    async def kick(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None) -> None:
        """
        Remove a user from the guild.

        Requires the ``KICK_MEMBERS`` permission.

        .. seealso:: :func:`novus.Guild.kick`

        Parameters
        ----------
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self.state.guild.remove_guild_member(
            self.guild.id,
            self.id,
            reason=reason,
        )

    async def ban(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            delete_message_seconds: int = MISSING) -> None:
        """
        Ban a user from the guild.

        Requires the ``BAN_MEMBERS`` permission.

        .. seealso:: :func:`novus.Guild.ban`

        Parameters
        ----------
        delete_message_seconds : int
            The number of seconds of messages you want to delete.
        reason : str | None
            The reason to be shown in the audit log.
        """

        updates: dict[str, Any] = {}

        if delete_message_seconds is not MISSING:
            updates['delete_message_seconds'] = delete_message_seconds

        await self.state.guild.create_guild_ban(
            self.guild.id,
            self.id,
            reason=reason,
            **updates
        )
        return

    async def create_dm_channel(self) -> DMChannel:
        return await self._user.create_dm_channel()

    async def _get_send_method(self) -> Callable[..., Awaitable[Any]]:
        return await self._user._get_send_method()


class ThreadMember:
    """
    A model representing a member inside of a thread.

    Attributes
    ----------
    id : int
        The ID of the user.
    thread_id : int
        The ID of the thread.
    join_timestamp : datetime.datetime
        The time that the user joined the thread.
    member : novus.GuildMember | None
        The guild member object.
    """

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.ThreadMember,
            guild_id: int | Snowflake | None = None):
        self.state = state

        # either set here or updated elsewhere
        self.thread_id: int = try_snowflake(data.get("id"))  # pyright: ignore
        self.id: int = try_snowflake(data.get("user_id"))  # pyright: ignore

        self.join_timestamp = parse_timestamp(data["join_timestamp"])
        self.member: GuildMember | None = None
        if "member" in data:
            self.member = GuildMember(
                state=self.state,
                data=data["member"],
                guild_id=guild_id,
            )
