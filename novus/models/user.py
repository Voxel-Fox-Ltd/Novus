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
from ..flags import UserFlags
from ..utils import cached_slot_property, generate_repr, try_enum, try_snowflake
from .api_mixins.user import UserAPIMixin
from .asset import Asset
from .mixins import Hashable

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import GuildMember as GuildMemberPayload
    from ..payloads import User as UserPayload
    from .abc import StateSnowflake
    from .guild_member import GuildMember

__all__ = (
    'User',
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
        '_guilds',
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
            self.flags = UserFlags(
                data.get('flags', 0) | data.get('public_flags', 0)
            )
        self.premium_type = try_enum(UserPremiumType, data.get('premium_type', 0))
        self._guilds: set[int] = set()

    __repr__ = generate_repr(('id', 'username', 'bot',))

    def __str__(self) -> str:
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

    @cached_slot_property('_cs_banner')
    def banner(self) -> Asset | None:
        if self.banner_hash is None:
            return None
        return Asset.from_user_banner(self)

    def _upgrade(self, data: GuildMemberPayload, guild: StateSnowflake) -> GuildMember:
        """
        Upgrade a user member to a guild member if we can.
        """

        from .guild_member import GuildMember
        v = GuildMember(
            state=self._state,
            data=data,
            user=self,
            guild=guild,
        )
        self._guilds.add(v.guild.id)
        return v

    def _to_user(self) -> User:
        return self
