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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import Locale, UserPremiumType
from ..flags import Permissions, UserFlags
from ..utils import (
    cached_slot_property,
    generate_repr,
    parse_timestamp,
    try_enum,
    try_snowflake,
)
from .api_mixins.user import GuildMemberAPIMixin, UserAPIMixin
from .asset import Asset
from .mixins import Hashable

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import GuildMember as GuildMemberPayload
    from ..payloads import ThreadMember as ThreadMemberPayload
    from ..payloads import User as UserPayload
    from .abc import StateSnowflake

__all__ = (
    'User',
    'GuildMember',
    'ThreadMember',
)


class User(Hashable, UserAPIMixin):
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
        '_state',
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
    )

    def __init__(self, *, state: HTTPConnection, data: UserPayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.username = data['username']
        self.discriminator = data['discriminator']
        self.avatar_hash = data.get('avatar')
        self.bot = data.get('bot', False)
        self.system = data.get('system', False)
        self.mfa_enabled = data.get('mfa_enabled', False)
        self.banner_hash = data.get('banner')
        self.accent_color = data.get('accent_color')
        self.locale = try_enum(Locale, data.get('locale'))
        self.verified = data.get('verified', False)
        self.email = data.get('email')
        self.flags = UserFlags(0)
        if 'flags' in data or 'public_flags' in data:
            self.flags = UserFlags(data.get('flags', 0) | data.get('public_flags', 0))
        self.premium_type = try_enum(UserPremiumType, data.get('premium_type', 0))

    __repr__ = generate_repr(('id', 'username', 'bot',))

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

    def _upgrade(self, data: GuildMemberPayload, guild: StateSnowflake) -> GuildMember:
        """
        Upgrade a user member to a guild member if we can.
        """

        return GuildMember(
            state=self._state,
            data=data,
            user=self._to_data(),
            guild=guild,
        )

    def _to_user(self) -> User:
        return self

    def _to_data(self) -> UserPayload:
        return {
            "id": str(self.id),
            "username": self.username,
            "discriminator": self.discriminator,
            "avatar": self.avatar_hash,
            "bot": self.bot,
            "system": self.system,
            "mfa_enabled": self.mfa_enabled,
            "banner": self.banner_hash,
            "accent_color": self.accent_color,
            # "locale": self.locale.value if self.locale else None,
            "verified": self.verified,
            "email": self.email,
            "flags": self.flags.value,
            "premium_type": self.premium_type.value,
        }


class GuildMember(User, GuildMemberAPIMixin):
    """
    A model for a guild member object.

    This model extends the `novus.User` object.

    Attributes
    ----------
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
    """

    __slots__ = (
        *User.__slots__,
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

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: GuildMemberPayload,
            guild: StateSnowflake,
            user: UserPayload | None = None):
        if user is not None:
            super().__init__(state=state, data=user)
        elif 'user' in data:
            super().__init__(state=state, data=data['user'])
        else:
            raise ValueError("Missing user data from member init")
        self.nick = data.get('nick')
        self.guild_avatar_hash = data.get('avatar')
        self.role_ids = [
            try_snowflake(d)
            for d in data['roles']
        ]
        self.joined_at = parse_timestamp(data['joined_at'])
        self.premium_since = parse_timestamp(data.get('premium_since'))
        self.deaf = data['deaf']
        self.mute = data['mute']
        self.pending = data.get('pending', False)
        self.permissions = None
        if 'permissions' in data:
            self.permissions = Permissions(int(data['permissions']))
        self.timeout_until = None
        if 'communication_disabled_until' in data:
            self.timeout_until = parse_timestamp(data['communication_disabled_until'])
        self.guild = guild

    @cached_slot_property('_cs_guild_avatar')
    def guild_avatar(self) -> Asset | None:
        if self.guild_avatar_hash is None:
            return None
        return Asset.from_guild_member_avatar(self)

    def _to_user(self) -> User:
        return User(
            state=self._state,
            data={
                "id": str(self.id),
                "username": self.username,
                "discriminator": self.discriminator,
                "avatar": self.avatar_hash,
                "bot": self.bot,
                "system": self.system,
                "mfa_enabled": self.mfa_enabled,
                "banner": self.banner_hash,
                "accent_color": self.accent_color,
                # "locale": self.locale.value if self.locale else None,
                "verified": self.verified,
                "email": self.email,
                "flags": self.flags.value,
                "premium_type": self.premium_type.value,
            }
        )


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

    def __init__(self, *, state: HTTPConnection, data: ThreadMemberPayload):
        self._state = state

        # either set here or updated elsewhere
        self.thread_id: int = try_snowflake(data.get("id"))  # pyright: ignore
        self.id: int = try_snowflake(data.get("user_id"))  # pyright: ignore

        self.join_timestamp = parse_timestamp(data["join_timestamp"])
        self.member: GuildMember | None = None
        if "member" in data:
            self.member = GuildMember(
                state=self._state,
                data=data["member"],
                guild=None,  # pyright: ignore
            )