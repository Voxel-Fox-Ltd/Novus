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

from datetime import datetime as dt
from datetime import timezone
from typing import overload

__all__ = (
    'DiscordDatetime',
    'parse_timestamp',
)


class DiscordDatetime(dt):
    """
    A simple wrapper around the `datetime.datetime` object with a ``naive``
    property so as to add a timezone object.

    Properties
    ----------
    naive : novus.utils.DiscordDatetime
    """

    @property
    def naive(self) -> DiscordDatetime:
        return self.astimezone(timezone.utc).replace(tzinfo=None)

    def deconstruct(self: dt) -> tuple:
        return (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
        )


@overload
def parse_timestamp(timestamp: str) -> dt:
    ...


@overload
def parse_timestamp(timestamp: None) -> None:
    ...


def parse_timestamp(timestamp: dt | str | None) -> dt | None:
    """
    Parse an isoformat timestamp from Discord.

    Parameters
    ----------
    timestamp : datetime.datetime | str | None
        The parsed timestamp.

    Returns
    -------
    datetime.datetime
        A datetime object with an added UTC timezone.
    """

    if timestamp is None:
        return None
    elif isinstance(timestamp, str):
        try:
            parsed = DiscordDatetime.strptime(
                timestamp,
                "%Y-%m-%dT%H:%M:%S.%f+00:00",
            )
        except ValueError:
            parsed = DiscordDatetime.strptime(
                timestamp,
                "%Y-%m-%dT%H:%M:%S+00:00",
            )
        parsed.replace(tzinfo=timezone.utc)
    elif isinstance(timestamp, dt):
        parsed = DiscordDatetime(*DiscordDatetime.deconstruct(timestamp))
    return parsed
