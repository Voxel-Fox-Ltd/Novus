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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from ._util import Snowflake
    from .user import User

__all__ = (
    'Sticker',
    'PartialSticker',
    'StickerPack',
)


class PartialSticker(TypedDict):  # Called "StickerItem" in the API
    id: Snowflake
    name: str
    format_type: str


class _StickerOptional(TypedDict, total=False):
    pack_id: Snowflake
    available: bool
    guild_id: Snowflake
    user: User
    sort_value: int


class Sticker(_StickerOptional):
    id: Snowflake
    name: str
    description: Optional[str]
    tags: str
    type: Literal[1, 2]
    format_type: Literal[1, 2, 3, 4]


class _StickerPackOptional(TypedDict, total=False):
    cover_sticker_id: Snowflake
    banner_asset_id: Snowflake


class StickerPack(_StickerPackOptional):
    id: Snowflake
    stickers: list[Sticker]
    name: str
    sku_id: Snowflake
    description: str
