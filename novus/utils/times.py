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

from datetime import datetime as dt
from datetime import timezone
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from ..enums.time import TimestampFormat

__all__ = (
    'DiscordDatetime',
    'parse_timestamp',
    'format_timestamp',
    'utcnow',
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
        return DiscordDatetime.fromtimestamp(self.timestamp())

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

    @property
    def mention(self) -> str:
        return format_timestamp(self)

    def format(self, style) -> str:
        return format_timestamp(self, style)


@overload
def parse_timestamp(timestamp: dt | str) -> DiscordDatetime:
    ...


@overload
def parse_timestamp(timestamp: None) -> None:
    ...


def parse_timestamp(timestamp: dt | str | None) -> DiscordDatetime | None:
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
        parsed = DiscordDatetime.fromisoformat(timestamp)
    elif isinstance(timestamp, dt):
        parsed = DiscordDatetime.fromisoformat(timestamp.isoformat())
    return parsed


def format_timestamp(
        timestamp: dt,
        style: TimestampFormat | str | None = None) -> str:
    """
    Format a timestamp into a rendered timestamp string.

    Parameters
    ----------
    timestamp : datetime.datetime
        The timestamp that you want to format.
    style : novus.TimestampFormat | str
        The format that you want to style the timestamp as.

    Returns
    -------
    str
        The formatted timestamp.
    """

    style_str: str | None
    if style is None:
        style_str = None
    elif isinstance(style, str):
        style_str = style
    else:
        style_str = style.value

    if style_str is None:
        return f"<t:{int(timestamp.timestamp())}>"
    return f"<t:{int(timestamp.timestamp())}:{style_str}>"


def utcnow() -> DiscordDatetime:
    """
    Get the current timestamp with a timezone applied to it.

    Returns
    -------
    datetime.datetime
        The created datetime.
    """

    ddt = DiscordDatetime.utcnow().replace(tzinfo=timezone.utc)
    return ddt
