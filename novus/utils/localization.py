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
from typing import TYPE_CHECKING, Any, Generator, Literal, overload

from typing_extensions import Self

from .missing import MISSING

if TYPE_CHECKING:
    from .. import Interaction

__all__ = (
    'Localization',
    'flatten_localization',
    'TranslatedString',
    'PluralTranslatedString',
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


_LOCALES = [
    "id",
    "da",
    "de",
    "en-GB",
    "en-US",
    "es-ES",
    "fr",
    "hr",
    "it",
    "lt",
    "hu",
    "nl",
    "no",
    "pl",
    "pt-BR",
    "ro",
    "fi",
    "sv-SE",
    "vi",
    "tr",
    "cs",
    "el",
    "bg",
    "ru",
    "uk",
    "hi",
    "th",
    "zh-CN",
    "ja",
    "zh-TW",
    "ko",
    "en-US",
    "zh-CN",
    "pt-BR",
]


class Localization:
    """
    A localizations class.
    """

    def __init__(
            self,
            current: dict[str, str] | dict[str, str] | None = None,
            **language_strings: str):
        self.localizations: dict[str, str] = {}
        if current:
            for k, v in current.items():
                self.__setitem__(k, v)
        for k, v in language_strings.items():
            self.__setitem__(k, v)

    def __bool__(self) -> bool:
        return bool(self.localizations)

    def __getitem__(self, key: str) -> str | None:
        return self.localizations.get(key)

    def __setitem__(self, key: str, value: str | None) -> None:
        if not value:
            self.localizations.pop(key, None)
        else:
            self.localizations[key] = value

    def items(self) -> Generator[tuple[str, str], None, None]:
        yield from self.localizations.items()

    def _to_data(self) -> dict[str, str]:
        return self.localizations

    @classmethod
    def _(cls, text: str) -> Self:
        """
        Return a generic localisation class for the given text.
        """

        created: dict[str, str] = {}
        for lc in _LOCALES:
            languages = [lc]
            if "-" in lc:
                languages.append(lc.split("-")[0])
            translated = TranslatedString.translate(text, languages, fallback=False)
            if translated is not None:
                created[lc] = translated
        return cls(created)


# any valid localisation type
LocType = dict[str, str] | Localization | None


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
            guild: int | bool = 1,
            user: int | bool = 0):
        self.original: str = original
        self.context: Interaction | None = context
        self.languages: list[str] | None
        self.languages = self._get_languages(
            guild=1_000 if guild is True else guild,
            user=1_000 if user is True else user,
        )

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
            ctx.locale,
            ctx.locale.split("-")[0],
        ]
        guild_languages: list[str] = []
        if guild and ctx.guild and ctx.guild_locale:
            guild_languages = [
                ctx.guild_locale,
                ctx.guild_locale.split("-")[0],
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
        return self.translate(self.original, self.languages)

    @overload
    @staticmethod
    def translate(
            text: str,
            languages: list[str] | None,
            fallback: Literal[True] = ...) -> str:
        ...

    @overload
    @staticmethod
    def translate(
            text: str,
            languages: list[str] | None,
            fallback: Literal[False] = ...) -> str | None:
        ...

    @staticmethod
    def translate(
            text: str,
            languages: list[str] | None,
            fallback: bool = True) -> str | None:
        try:
            v = gettext.translation(
                domain="main",
                localedir="./locales",
                languages=languages,
                fallback=fallback,
            ).gettext(text)
            if v == text and not fallback:
                return None
            return v
        except OSError:
            return None


class PluralTranslatedString(TranslatedString):

    def __init__(
            self,
            original: str,
            plural_string: str,
            number: int,
            *,
            context: Interaction[Any] | None = None,
            guild: int | bool = 1,
            user: int | bool = 0):
        super().__init__(original, context=context, guild=guild, user=user)
        self.plural_string = plural_string
        self.number = number

    def __str__(self) -> str:
        return self.plural_translate(self.original, self.plural_string, self.number, self.languages)

    @staticmethod
    def plural_translate(
            text: str,
            plural_text: str,
            number: int,
            languages: list[str] | None,
            fallback: bool = True) -> str:
        try:
            return gettext.translation(
                domain="main",
                localedir="./locales",
                languages=languages,
                fallback=fallback,
            ).ngettext(text, plural_text, number)
        except OSError:
            return ""
