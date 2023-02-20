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

__all__ = (
    'ApplicationCommandOption',
    'ApplicationCommandChoice',
)


class ApplicationCommandOption:

    def __init__(self, *args, **kwargs):
        ...


class ApplicationCommandChoice:
    """
    A choice object for application commands.

    Parameters
    ----------
    name : str
        The name of the choice.
    value : str | int | float
        The value associated with the choice.

        .. note::

            Large numbers (those in BIGINT range, including IDs) will be
            truncated by Discord - it's recommended that you use a string in
            their place.

    Attributes
    ----------
    name : str
        The name of the choice.
    value : str | int | float
        The value associated with the choice.
    """

    def __init__(self, name: str, value: str | int | float):
        self.name = name
        self.value = value
