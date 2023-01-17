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

import os

import dotenv

from ..utils import generate_repr

__all__ = (
    'Route',
)


dotenv.load_dotenv()


class Route:

    __slots__ = (
        'method',
        'resource',
        'kwargs',
    )

    BASE = os.getenv(
        "NOVUS_API_URL",
        "https://discord.com/api/v10",
    )

    def __init__(self, method: str, resource: str, **kwargs):
        self.method = method
        self.resource = resource
        self.kwargs = kwargs

    @property
    def path(self):
        return self.resource.format_map(self.kwargs)

    @property
    def url(self):
        return self.BASE + self.path

    def __str__(self) -> str:
        return self.url

    __repr__ = generate_repr(
        (
            "method",
            ("resource", "path",),
        )
    )
