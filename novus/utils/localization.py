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

from ..enums import Locale

if TYPE_CHECKING:
    from .. import payloads

__all__ = (
    'Localization',
)


class Localization:
    """
    A localizations class.
    """

    def __init__(
            self,
            current: dict[str, str] | dict[Locale, str] | None = None,
            **language_strings: str):
        self.localizations: dict[Locale, str] = {}
        if current:
            for k, v in current.items():
                self.__setitem__(k, v)
        for k, v in language_strings.items():
            self.__setitem__(k, v)

    def __bool__(self) -> bool:
        return bool(self.localizations)

    def __getitem__(self, key: str | Locale) -> str | None:
        if isinstance(key, str):
            key = Locale(key)
        return self.localizations.get(key)

    def __setitem__(self, key: str | Locale, value: str | None) -> None:
        if isinstance(key, str):
            key = Locale(key)
        if not value:
            self.localizations.pop(key, None)
        else:
            self.localizations[key] = value

    def _to_data(self) -> dict[payloads.Locale, str]:
        return {
            i.value: o
            for i, o in self.localizations.items()
        }
