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

from ..enums import StickerFormat
from ..utils import cached_slot_property, try_snowflake
from .api_mixins.sticker import StickerAPIMixin
from .asset import Asset

if TYPE_CHECKING:
    from .. import Guild, payloads
    from ..api import HTTPConnection
    from . import api_mixins as amix

__all__ = (
    'Sticker',
)


class Sticker(StickerAPIMixin):
    """
    A model for a sticker.

    Attributes
    ----------
    id : int
        The ID of the sticker.
    pack_id : int | None
        The ID of the pack that the sticker came in, for standard stickers.
    name : str
        The name of the sticker.
    description : str
        The description of the sticker.
    format_type : novus.StickerFormat
        The format for the sticker.
    available : bool
        Whether or not the sticker can be used. May be ``False`` due to loss of
        nitro boosts.
    asset : novus.Asset
        The asset associated with the sticker.
    guild : novus.Guild | None
        The guild (or a data container for the ID) that the emoji came from.
        May be ``None`` if the sticker does not come from a guild.
    """

    __slots__ = (
        '_state',
        'id',
        'pack_id',
        'name',
        'description',
        # 'type',
        'format_type',
        'available',
        'guild',

        '_cs_asset',
    )

    id: int
    pack_id: int | None
    name: str
    description: str | None
    format_type: StickerFormat
    available: bool
    guild: Guild | amix.GuildAPIMixin | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Sticker | payloads.PartialSticker):
        self._state = state
        self.id: int = try_snowflake(data['id'])
        self.pack_id: int | None = try_snowflake(data.get('pack_id'))
        self.name: str = data['name']
        self.description: str | None = data.get('description')
        # self.type: StickerType = StickerType(data['type'])
        self.format_type: StickerFormat = StickerFormat(data['format_type'])
        self.available: bool = data.get('available', True)
        self.guild = None
        if "guild_id" in data:
            self.guild = self._state.cache.get_guild(
                data["guild_id"],  # pyright: ignore  # Thanks Pyright
                or_object=True,
            )

    @cached_slot_property('_cs_asset')
    def asset(self) -> Asset:
        return Asset.from_sticker(self)
