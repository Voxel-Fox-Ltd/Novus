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
from typing import Protocol, overload

__all__ = (
    'DiscordDatetime',
    'parse_timestamp',
    'format_timestamp',
    'utcnow',
    'now',
)


# mypy doesn't like the protocol we have in models.abc so we will make a new
# in-class protocol for just here
class Snowflake(Protocol):
    id: int


class DiscordDatetime(dt):
    """
    A simple wrapper around the `datetime.datetime` object with a ``naive``
    property so as to add a timezone object.

    Attributes
    ----------
    naive : novus.utils.DiscordDatetime
        The associated naive datetime for the timestamp.

    Properties
    ----------
    mention : str
        A rendered timestamp string. Shorthand for ``.format()``.
    """

    @staticmethod
    def from_datetime(datetime: dt) -> DiscordDatetime:
        return parse_timestamp(datetime)

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
    def snowflake(self) -> str:
        """
        Make a fake snowflake that reflects the given timestamp.
        """

        return str(int((self.timestamp() * 1e3 - 1_420_070_400_000) * 1e4) << 22)

    @property
    def mention(self) -> str:
        return format_timestamp(self)

    def format(self, style: str | None = None) -> str:
        """
        Format the timestamp into a rendered timestamp string.

        Parameters
        ----------
        style : str
            The format that you want to style the timestamp as.

            .. seealso:: `novus.TimestampFormat`

        Returns
        -------
        str
            The formatted timestamp.
        """

        return format_timestamp(self, style)


@overload
def parse_timestamp(timestamp: dt | str | int | Snowflake) -> DiscordDatetime:
    ...


@overload
def parse_timestamp(timestamp: None) -> None:
    ...


def parse_timestamp(timestamp: dt | str | int | Snowflake | None) -> DiscordDatetime | None:
    """
    Parse an isoformat timestamp from Discord.

    Parameters
    ----------
    timestamp : datetime.datetime | str | int | novus.types.Snowflake | None
        The timstamp to parse. Either a datetime, an ID or an object that
        follows the snowflake protocol (ie it implements an ID).

    Returns
    -------
    datetime.datetime
        A datetime object with an added UTC timezone.
    """

    if timestamp is None:
        return None
    elif isinstance(timestamp, str):
        if timestamp.isdigit():
            return (
                DiscordDatetime
                .fromtimestamp(((int(timestamp) >> 22) + 1_420_070_400_000) / 1e3)
                .replace(tzinfo=timezone.utc)
            )
        return DiscordDatetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
    elif isinstance(timestamp, int):
        return (
            DiscordDatetime
            .fromtimestamp(((timestamp >> 22) + 1_420_070_400_000) / 1e3)
            .replace(tzinfo=timezone.utc)
        )
    elif isinstance(timestamp, (str, int)):
        return (
            DiscordDatetime
            .fromtimestamp(((int(timestamp) >> 22) + 1_420_070_400_000) / 1e3)
            .replace(tzinfo=timezone.utc)
        )
    elif isinstance(timestamp, dt):
        return (
            DiscordDatetime.fromisoformat(timestamp.isoformat())
            .replace(tzinfo=timezone.utc)
        )
    elif hasattr(timestamp, "id"):
        return (
            DiscordDatetime
            .fromtimestamp(((timestamp.id >> 22) + 1_420_070_400_000) / 1e3)
            .replace(tzinfo=timezone.utc)
        )
    raise ValueError


def format_timestamp(
        timestamp: dt,
        style: str | None = None) -> str:
    """
    Format a timestamp into a rendered timestamp string.

    Parameters
    ----------
    timestamp : datetime.datetime
        The timestamp that you want to format.
    style : str
        The format that you want to style the timestamp as.

        .. seealso:: `novus.TimestampFormat`

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

    if style_str is None:
        return f"<t:{int(timestamp.timestamp())}>"
    return f"<t:{int(timestamp.timestamp())}:{style_str}>"


def utcnow() -> DiscordDatetime:
    """
    Get the current timestamp with a timezone applied to it.

    Shorthand for ``datetime.datetime.now(datetime.timezone.utc)``.

    Returns
    -------
    datetime.datetime
        The created datetime.
    """

    ddt = DiscordDatetime.now(timezone.utc)
    return ddt


now = utcnow
