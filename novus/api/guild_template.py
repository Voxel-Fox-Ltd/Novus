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

from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from ._http import HTTPConnection

__all__ = (
    'GuildTemplateHTTPConnection',
)


class GuildTemplateHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_guild_template(self, template_code: str) -> NoReturn:
        raise NotImplementedError()

    async def create_guild_from_template(self, template_code: str) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_templates(self, guild_id: int) -> NoReturn:
        raise NotImplementedError()

    async def create_guild_templatte(self, guild_id: int) -> NoReturn:
        raise NotImplementedError()

    async def sync_guild_template(self, guild_id: int, template_code: str) -> NoReturn:
        raise NotImplementedError()

    async def modify_guild_template(self, guild_id: int, template_code: str) -> NoReturn:
        raise NotImplementedError()

    async def delete_guild_template(self, guild_id: int, template_code: str) -> NoReturn:
        raise NotImplementedError()
