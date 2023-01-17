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

from typing import TYPE_CHECKING, Literal, TypeAlias

import os

import dotenv

from ..utils import MISSING, generate_repr

if TYPE_CHECKING:
    from .guild import Guild, OauthGuild, GuildPreview
    from .emoji import Emoji
    from .role import Role
    from .sticker import Sticker

    AnyFullGuild: TypeAlias = Guild | OauthGuild
    AnyGuild: TypeAlias = AnyFullGuild | GuildPreview

__all__ = (
    'Asset',
)


dotenv.load_dotenv()


class Asset:
    """
    A representation of a discord image model.

    Attributes
    ----------
    resource : str
        The path assicated with the URL.
    animated : bool
        Whether or not the asset is animated.
    """

    BASE = os.getenv(
        "NOVUS_API_URL",
        "https://cdn.discordapp.com"
    )

    __slots__ = (
        'resource',
        'animated',
        'default_format',
    )

    def __init__(
            self,
            resource: str,
            animated: bool = MISSING,
            default_format: str | None = None):
        self.resource: str = resource
        if animated is MISSING:
            animated = self.resource.split("/")[-1].startswith("a_")
        self.animated: bool = animated
        self.default_format = default_format or "webp"

    def __str__(self) -> str:
        return self.get_url()

    __repr__ = generate_repr(('resource', 'animated',))

    def get_url(
            self,
            format: Literal["webp", "jpg", "jpeg", "png", "gif", "json"] = MISSING,
            size: int = MISSING) -> str:
        """
        Get the URL for the image with different formatting and size than the
        CDN default.

        Parameters
        ----------
        format : str
            The format that you want to get the URL as.
        """

        return (
            f"{self.BASE}{self.resource}."
            f"{format or self.default_format}"
            f"?size={size or 1024}"
        )

    @classmethod
    def from_guild_icon(cls, guild: AnyGuild) -> Asset:
        return cls(f"/icons/{guild.id}/{guild.icon_hash}")

    @classmethod
    def from_guild_splash(cls, guild: AnyGuild) -> Asset:
        return cls(f"/splashes/{guild.id}/{guild.splash_hash}")

    @classmethod
    def from_guild_discovery_splash(cls, guild: AnyGuild) -> Asset:
        return cls(f"/discovery-splashes/{guild.id}/{guild.discovery_splash_hash}")

    @classmethod
    def from_guild_banner(cls, guild: AnyFullGuild) -> Asset:
        return cls(f"/banners/{guild.id}/{guild.banner_hash}")

    @classmethod
    def from_emoji(cls, emoji: Emoji) -> Asset:
        return cls(f"/emojis/{emoji.id}", animated=emoji.animated)

    @classmethod
    def from_role(cls, role: Role) -> Asset:
        return cls(f"/role-icons/{role.id}/{role.icon_hash}")

    @classmethod
    def from_sticker(cls, sticker: Sticker) -> Asset:
        return cls(f"/stickers/{sticker.id}")