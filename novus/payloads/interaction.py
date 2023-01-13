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

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from ._util import Snowflake
    from .user import User, GuildMember

__all__ = (
    'InteractionType',
    'MessageInteraction',
)


InteractionType = Literal[
    1,  # PING
    2,  # APPLICATION_COMMAND
    3,  # MESSAGE_COMPONENT
    4,  # APPLICATION_COMMAND_AUTOCOMPLETE
    5,  # MODAL_SUBMIT
]


class _MessageInteractionOptional(TypedDict, total=False):
    member: GuildMember


class MessageInteraction(_MessageInteractionOptional):
    id: Snowflake
    type: InteractionType
    name: str
    user: User
