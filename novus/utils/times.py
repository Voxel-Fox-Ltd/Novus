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

from datetime import datetime as dt, timezone
from typing import overload

__all__ = (
    'DiscordDatetime',
    'parse_timestamp',
)


class DiscordDatetime(dt):

    @property
    def naive(self) -> DiscordDatetime:
        return self.replace(tzinfo=timezone.utc)


@overload
def parse_timestamp(timestamp: str) -> dt:
    ...


@overload
def parse_timestamp(timestamp: None) -> None:
    ...


def parse_timestamp(timestamp: str | None) -> dt | None:
    """
    Parse an isoformat timestamp from Discord.

    Parameters
    ----------
    timestamp : str
        The parsed timestamp.

    Returns
    -------
    datetime.datetime
        A datetime object with an added UTC timezone.
    """

    if timestamp is None:
        return None
    parsed = DiscordDatetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f+00:00")
    parsed.replace(tzinfo=timezone.utc)
    return parsed
