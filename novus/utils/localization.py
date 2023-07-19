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

import gettext
from typing import TYPE_CHECKING, Any, Literal

from ..enums import Locale
from .missing import MISSING

if TYPE_CHECKING:
    from .. import Interaction, payloads

__all__ = (
    'Localization',
    'flatten_localization',
    'TranslatedString',
)


def flatten_localization(d: LocType) -> Localization:
    if d is MISSING or d is None:
        return Localization()
    elif isinstance(d, Localization):
        return d
    elif isinstance(d, dict):
        return Localization(d)
    else:
        raise TypeError()


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


# any valid localisation type
LocType = dict[str, str] | dict[Locale, str] | Localization | None


class TranslatedString:
    """
    An object to help with translation of strings.

    Takes an input, takes a relevant context, gettexts the hell out of it.
    """

    def __init__(
            self,
            original: str,
            *,
            context: Interaction[Any] | None = None,
            guild: int | Literal[False] = 1,
            user: int | Literal[False] = 0):
        self.original: str = original
        self.context: Interaction | None = context
        self.languages: list[str] | None
        self.languages = self._get_languages(guild=guild, user=user)

    def _get_languages(
            self,
            *,
            guild: int | Literal[False],
            user: int | Literal[False]) -> list[str]:
        """
        Get the languages for to use for the translation.

        `guild` and `user` are in priority order (defaulting to guild
        being higher priority), or ``False`` to disable.
        """

        # We can only reutrn things if we have a context to give
        if not (ctx := self.context):
            return []

        # Work out what languages we even have available
        user_languages: list[str] = [
            ctx.locale.value,
            ctx.locale.value.split("-")[0],
        ]
        guild_languages: list[str] = []
        if guild and ctx.guild and ctx.guild_locale:
            guild_languages = [
                ctx.guild_locale.value,
                ctx.guild_locale.value.split("-")[0],
            ]

        # Work out what we can return
        if guild is False and user is False:
            return []
        elif user is False:
            return guild_languages
        elif guild is False:
            return user_languages
        else:

            # Return languages in order priority
            if user == guild or guild > user:
                return [*guild_languages, *user_languages]
            else:
                return [*user_languages, *guild_languages]

    def __str__(self) -> str:
        return gettext.translation(
            domain="main",
            localedir="./locales",
            languages=self.languages,
            fallback=True,
        ).gettext(self.original)
