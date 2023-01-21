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

from .asset import Asset
from ..enums import sticker as sticker_enums
from ..utils import try_snowflake, cached_slot_property

if TYPE_CHECKING:
    from .abc import Snowflake
    from ..payloads import Sticker as StickerPayload
    from ..api import HTTPConnection

__all__ = (
    'Sticker',
)


class Sticker:
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
    type : novus.enums.StickerType
        The type of the sticker.
    format_type : novus.enums.StickerFormat
        The format for the sticker.
    available : bool
        Whether or not the sticker can be used. May be ``False`` due to loss of
        nitro boosts.
    guild_id : int | None
        The ID of the guild associated with the sticker.
    asset : novus.models.Asset
        The asset associated with the sticker.
    guild : novus.models.abc.Snowflake | novus.models.Guild
        The guild (or a data container for the ID) that the emoji came from.
    """

    __slots__ = (
        '_state',
        'id',
        'pack_id',
        'name',
        'description',
        'type',
        'format_type',
        'available',
        'guild',

        '_cs_asset',
    )

    def __init__(self, *, state: HTTPConnection, data: StickerPayload, guild: Snowflake):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.pack_id = try_snowflake(data.get('pack_id'))
        self.name = data['name']
        self.description = data['description']
        self.type = sticker_enums.StickerType(data['type'])
        self.format_type = sticker_enums.StickerFormat(data['format_type'])
        self.available = data.get('available', True)
        self.guild = guild

    @cached_slot_property('_cs_asset')
    def asset(self) -> Asset:
        return Asset.from_sticker(self)
