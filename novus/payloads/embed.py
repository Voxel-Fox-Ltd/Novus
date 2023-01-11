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

from typing import Literal, TypedDict

__all__ = (
    'Embed',
    'EmbedType',
)


EmbedType = Literal[
    "rich",
    "image",
    "video",
    "gifv",
    "article",
    "link",
]


class _PossiblyProxiedMedia(TypedDict, total=False):
    proxy_url: str
    height: int
    width: int


class _EmbedMedia(_PossiblyProxiedMedia):
    url: str


class _EmbedFooterOptional(TypedDict, total=False):
    icon_url: str
    proxy_icon_url: str


class _EmbedFooter(_EmbedFooterOptional):
    text: str


class _EmbedVideo(_PossiblyProxiedMedia, total=False):
    url: str


class _EmbedProvider(TypedDict, total=False):
    name: str
    url: str


class _EmbedAuthorOptional(TypedDict, total=False):
    url: str
    icon_url: str
    proxy_icon_url: str


class _EmbedAuthor(_EmbedAuthorOptional):
    name: str


class _EmbedFieldOptional(TypedDict, total=False):
    inline: bool


class _EmbedField(_EmbedFieldOptional):
    name: str
    value: str


class Embed(TypedDict, total=False):
    title: str
    type: EmbedType
    description: str
    url: str
    timestamp: str
    color: int
    footer: _EmbedFooter
    image: _EmbedMedia
    thumbnail: _EmbedMedia
    video: _EmbedVideo
    provider: _EmbedProvider
    author: _EmbedAuthor
    fields: list[_EmbedField]
