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

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from ._util import Snowflake, Timestamp

__all__ = (
    'SKU',
    'Entitlement',
)


class SKU(TypedDict):
    id: Snowflake
    type: int
    application_id: Snowflake
    name: str
    slug: str
    flags: int


class Entitlement(TypedDict):
    id: Snowflake
    sku_id: Snowflake
    application_id: Snowflake
    user_id: NotRequired[Snowflake]
    type: int
    deleted: bool
    starts_at: NotRequired[Timestamp]
    ends_at: NotRequired[Timestamp]
    guild_id: NotRequired[Snowflake]
    consumed: NotRequired[bool]
