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

from typing import TYPE_CHECKING

from ..utils import DiscordDatetime, parse_timestamp, try_snowflake, try_id
from ..flags import SKUFlags
from ..enums import SKUType

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from .. import payloads

__all__ = (
    'SKU',
    'Entitlement',
)


class SKU:
    """
    A Discord stock-keeping unit - an item that can be purchased.

    Attributes
    ----------
    id : int
        The ID of the SKU.
    type : int
        The type of the SKU.

        .. seealso: `novus.SKUType`
    application_id : int
        The ID of the application that the SKU is associated with.
    name : str
        The name of the SKU.
    slug : str
        A system-generated URL slug based on the SKU's name.
    flags : `novus.SKUFlags`
        Flags associated with the SKU.
    """

    def __init__(self, *, data: payloads.SKU, state: HTTPConnection):
        self.id: int = try_snowflake(data["id"])
        self.type: SKUType = SKUType(data["type"])
        self.application_id: int = try_snowflake(data["application_id"])
        self.name: str = data["name"]
        self.slug: str = data["slug"]
        self.flags: SKUFlags = SKUFlags(data["flags"])

    # API methods

    async def list_skus(cls, state: HTTPConnection) -> list[SKU]:
        """
        List all of the SKUs that the application has created.

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        """

        return await state.monetization.list_skus(state.application_id)


class Entitlement:
    """
    A purchase that a user has made associated with your application.

    Attributes
    ----------
    id : int
        The ID of the entitlement.
    sku_id : int
        The ID of the purchased SKU.
    application_id : int
        The ID of the application that the SKU belongs to.
    user_id : int | None
        The user that was granted access to the entitlement's SKU.
    type : int
        The type of entitlement.

        .. seealso:: `novus.EntitlementType`
    deleted : bool
        Whether or not the entitlement was deleted.
    starts_at : `novus.utils.DiscordDatetime` | None
        The date from which the entitlement is valid. Not present on test
        entitlements.
    ends_at : `novus.utils.DiscordDatetime` | None
        The date at which the entitlement is no longer valid. Not present on
        test entitlements.
    guild_id : int | None
        The ID of the guild that was granted access to the entitlement's SKU.
    consumed : bool | None
        For consumable items, whether or not the entitlement has been consumed.
    """

    __slots__ = (
        'id',
        'sku_id',
        'application_id',
        'user_id',
        'type',
        'deleted',
        'starts_at',
        'ends_at',
        'guild_id',
        'consumed',
        'state',
    )

    def __init__(self, *, data: payloads.Entitlement, state: HTTPConnection):
        self.id: int = try_snowflake(data["id"])
        self.sku_id: int = try_snowflake(data["sku_id"])
        self.application_id: int = try_snowflake(data["application_id"])
        self.user_id: int | None = try_snowflake(data.get("user_id"))
        self.type: int = data["type"]
        self.deleted: bool = data["deleted"]
        self.starts_at: DiscordDatetime | None = parse_timestamp(data.get("starts_at"))
        self.ends_at: DiscordDatetime | None = parse_timestamp(data.get("ends_at"))
        self.guild_id: int | None = data.get("guild_id")
        self.consumed: bool | None = data.get("consumed")
        self.state = state

    # API methods

    # @classmethod
    # async def list_entitlements(
    #         cls,
    #         state: HTTPConnection,
    #         *,
    #         limit: int = 100,
    #         around: int | abc.Snowflake | Message = MISSING,
    #         before: int | abc.Snowflake | Message = MISSING,
    #         after: int | abc.Snowflake | Message = MISSING) -> list[Entitlement]:
    #     """
    #     Get a number of messages from the channel.

    #     Parameters
    #     ----------
    #     limit : int
    #         The number of messages that you want to get. Maximum 100.
    #     around : int | novus.abc.Snowflake
    #         Get messages around this ID.
    #         Only one of ``around``, ``before``, and ``after`` can be set.
    #     before : int | novus.abc.Snowflake
    #         Get messages before this ID.
    #         Only one of ``around``, ``before``, and ``after`` can be set.
    #     after : int | novus.abc.Snowflake
    #         Get messages after this ID.
    #         Only one of ``around``, ``before``, and ``after`` can be set.

    #     Returns
    #     -------
    #     list[novus.Message]
    #         The messages that were retrieved.
    #     """

    #     params: dict[str, int] = {}
    #     add_not_missing(params, "limit", limit)
    #     add_not_missing(params, "around", around, try_id)
    #     add_not_missing(params, "before", before, try_id)
    #     add_not_missing(params, "after", after, try_id)
    #     return await self.state.channel.get_channel_messages(
    #         self.id,
    #         **params,
    #     )

    # @classmethod
    # def entitlement(
    #         cls,
    #         state: HTTPConnection,
    #         *,
    #         limit: int | None = 100,
    #         before: int | abc.Snowflake | Message = MISSING,
    #         after: int | abc.Snowflake | Message = MISSING) -> APIIterator[Message]:
    #     """
    #     Get an iterator of messages from a channel.

    #     Examples
    #     --------

    #     .. code-block::

    #         async for message in channel.messages(limit=1_000):
    #             print(message.content)

    #     .. code-block::

    #         messages = await channel.messages(limit=200).flatten()

    #     Parameters
    #     ----------
    #     limit : int
    #         The number of messages that you want to get.
    #     before : int | novus.abc.Snowflake
    #         Get messages before this ID.
    #         Only one of ``around``, ``before``, and ``after`` can be set.
    #     after : int | novus.abc.Snowflake
    #         Get messages after this ID.
    #         Only one of ``around``, ``before``, and ``after`` can be set.

    #     Returns
    #     -------
    #     APIIterator[novus.Message]
    #         The messages that were retrieved, as a generator.
    #     """

    #     from ..api import APIIterator  # circular import
    #     return APIIterator(
    #         method=self.fetch_messages,
    #         before=before,
    #         after=after,
    #         limit=limit,
    #         method_limit=100,
    #     )

    async def consume(self) -> None:
        """
        Consume the entitlement.
        """

        await self.state.monetization.consume_entitlement(
            self.application_id,
            self.id,
        )
        self.consumed = True
        return None
