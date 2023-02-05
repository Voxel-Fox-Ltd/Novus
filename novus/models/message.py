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

from dataclasses import dataclass
from datetime import datetime as dt
from typing import TYPE_CHECKING, Any

from ..utils import cached_slot_property, get_mime_type_for_image, parse_timestamp

if TYPE_CHECKING:
    import io
    import pathlib

    from ..payloads.embed import Embed as EmbedPayload
    from ..payloads.embed import _EmbedAuthor as AuthorPayload
    from ..payloads.embed import _EmbedField as FieldPayload
    from ..payloads.embed import _EmbedFooter as FooterPayload
    from ..payloads.embed import _EmbedMedia as MediaPayload

__all__ = (
    'Embed',
    'MessageReference',
    'Message',
    'AllowedMentions',
    'File',
)


@dataclass
class EmbedFooter:
    text: str
    icon_url: str | None = None
    proxy_icon_url: str | None = None

    def _to_data(self) -> FooterPayload:
        v: FooterPayload = {
            "text": self.text
        }
        if self.icon_url:
            v["icon_url"] = self.icon_url
        return v


@dataclass
class EmbedMedia:
    url: str
    proxy_url: str | None = None
    height: int | None = None
    width: int | None = None

    def _to_data(self) -> MediaPayload:
        return {
            "url": self.url
        }


@dataclass
class EmbedVideo:
    url: str | None = None
    proxy_url: str | None = None
    height: int | None = None
    width: int | None = None


@dataclass
class EmbedProvider:
    name: str | None = None
    url: str | None = None


@dataclass
class EmbedAuthor:
    name: str
    url: str | None = None
    icon_url: str | None = None
    proxy_icon_url: str | None = None

    def _to_data(self) -> AuthorPayload:
        v: AuthorPayload = {
            "name": self.name
        }
        if self.url:
            v["url"] = self.url
        if self.icon_url:
            v["icon_url"] = self.icon_url
        return v


@dataclass
class EmbedField:
    name: str
    value: str
    inline: bool = True

    def _to_data(self) -> FieldPayload:
        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline,
        }


class Embed:
    """
    A model for an embed object.

    Parameters
    ----------
    title: str
        The title on the embed.
    description: str
        The description of the embed.
    url: str
        The url of the embed, attached to the title.
    timestamp: datetime.datetime
        The timestamp in the footer of the bot.
    color: int
        The color of the embed.

    Attributes
    ----------
    title : str | None
        The title of the embed.
    type : str | None
        The type of the embed.
    description : str | None
        The description of the embed.
    url : str | None
        The URL of the embed.
    timestamp : datetime.datetime | None
        The timestamp in the embed footer.
    color : int | None
        The colour integer of the embed.
    footer : object | None
        The footer of the embed.
        An object containing the following attributes:

        * ``text``: `str`
        * ``icon_url``: `str` | `None`
        * ``proxy_icon_url``: `str` | `None`
    image : object | None
        The image added to the embed.
        An object containing the following attributes:

        * ``url``: `str`
        * ``proxy_url``: `str` | `None`
        * ``height``: `int` | `None`
        * ``width``: `int` | `None`
    thumbnail : object | None
        The image added to the embed.
        An object containing the following attributes:

        * ``url``: `str`
        * ``proxy_url``: `str` | `None`
        * ``height``: `int` | `None`
        * ``width``: `int` | `None`
    video : object | None
        The video added to the embed.
        An object containing the following attributes:

        * ``url``: `str` | `None`
        * ``proxy_url``: `str` | `None`
        * ``height``: `int` | `None`
        * ``width``: `int` | `None`
    provider : object | None
        The provider information.
        An object containing the following attributes:

        * ``name``: `str` | `None`
        * ``url``: `str` | `None`
    author : object | None
        The author of the embed.
        An object containing the following attributes:

        * ``name``: `str`
        * ``url``: `str` | `None`
        * ``icon_url``: `str` | `None`
        * ``proxy_icon_url``: `str` | `None`
    fields : list[object]
        A list of fields added to the embed.
        An a field is an object containing the following attributes:

        * ``name``: `str`
        * ``value``: `str`
        * ``inline``: `bool`
    """

    def __init__(
            self,
            *,
            title: str | None = None,
            type: str = "rich",
            description: str | None = None,
            url: str | None = None,
            timestamp: dt | None = None,
            color: int | None = None) -> None:
        self.title: str | None = title
        self.type: str = type
        self.description: str | None = description
        self.url: str | None = url
        self.timestamp: dt | None = timestamp
        self.color: int | None = color

        self._footer: EmbedFooter | None = None
        self._image: EmbedMedia | None = None
        self._thumbnail: EmbedMedia | None = None
        self._video: EmbedVideo | None = None
        self._provider: EmbedProvider | None = None
        self._author: EmbedAuthor | None = None
        self._fields: list[EmbedField] = []

    def _to_data(self) -> EmbedPayload:
        v: EmbedPayload = {}
        if self.title is not None:
            v["title"] = self.title
        if self.description is not None:
            v["description"] = self.description
        if self.url is not None:
            v["url"] = self.url
        if self.timestamp is not None:
            v["timestamp"] = self.timestamp.isoformat()
        if self.color is not None:
            v["color"] = self.color
        if self._footer is not None:
            v["footer"] = self._footer._to_data()
        if self._image is not None:
            v["image"] = self._image._to_data()
        if self._thumbnail is not None:
            v["thumbnail"] = self._thumbnail._to_data()
        if self._author is not None:
            v["author"] = self._author._to_data()
        if self._fields is not None:
            v["fields"] = [i._to_data() for i in self._fields]
        return v

    @classmethod
    def _from_data(cls, data: EmbedPayload) -> Embed:
        timestamp = data.get("timestamp")
        if timestamp is not None:
            timestamp = parse_timestamp(timestamp)
        embed = cls(
            title=data.get("title"),
            type=data.get("type") or "rich",
            description=data.get("description"),
            url=data.get("url"),
            timestamp=timestamp,
            color=data.get("color"),
        )
        if "footer" in data:
            embed._footer = EmbedFooter(**data["footer"])
        if "image" in data:
            embed._image = EmbedMedia(**data["image"])
        if "thumbnail" in data:
            embed._thumbnail = EmbedMedia(**data["thumbnail"])
        if "video" in data:
            embed._video = EmbedVideo(**data["video"])
        if "provider" in data:
            embed._provider = EmbedProvider(**data["provider"])
        if "author" in data:
            embed._author = EmbedAuthor(**data["author"])
        if "fields" in data:
            embed._fields = [
                EmbedField(**d)
                for d in data["fields"]
            ]
        return embed

    @property
    def footer(self) -> EmbedFooter | None:
        return self._footer

    def set_footer(
            self,
            text: str,
            *,
            icon_url: str | None = None) -> Embed:
        """
        Set the footer of the embed.

        Parameters
        ----------
        text : str
            The text to be added to the footer. Does not support markdown.
        icon_url : str | None
            The url of the icon to be used in the footer. Only supports HTTP(S)
            and attachments.
        """

        self._footer = EmbedFooter(
            text=text,
            icon_url=icon_url,
        )
        return self

    def remove_footer(self) -> Embed:
        """
        Remove the footer of the embed.
        """

        self._footer = None
        return self

    @property
    def image(self) -> EmbedMedia | None:
        return self._image

    def set_image(self, url: str) -> Embed:
        """
        Set an image for the embed.

        Parameters
        ----------
        url : str
            The source url of the image. Only supports HTTP(S) and attachments.
        """

        self._image = EmbedMedia(url)
        return self

    def remove_image(self) -> Embed:
        """
        Remove the image of the embed.
        """

        self._image = None
        return self

    @property
    def thumbnail(self) -> EmbedMedia | None:
        return self._thumbnail

    def set_thumbnail(self, url: str) -> Embed:
        """
        Set an thumbnail for the embed.

        Parameters
        ----------
        url : str
            The source url of the thumbnail. Only supports HTTP(S) and
            attachments.
        """

        self._thumbnail = EmbedMedia(url)
        return self

    def remove_thumbnail(self) -> Embed:
        """
        Remove the thumbnail of the embed.
        """

        self._thumbnail = None
        return self

    @property
    def video(self) -> EmbedVideo | None:
        return self._video

    @property
    def provider(self) -> EmbedProvider | None:
        return self._provider

    @property
    def author(self) -> EmbedAuthor | None:
        return self._author

    def set_author(
            self,
            name: str,
            *,
            url: str | None = None,
            icon_url: str | None = None) -> Embed:
        """
        Set the author of the embed.

        Parameters
        ----------
        name : str
            The name of the author in the embed.
        url : str | None
            The URL attached to the author's name in the embed.
        icon_url : str | None
            The url of the author's icon.
        """

        self._author = EmbedAuthor(
            name=name,
            url=url,
            icon_url=icon_url,
        )
        return self

    def remove_author(self) -> Embed:
        """
        Remove the author of the embed.
        """

        self._author = None
        return self

    @property
    def fields(self) -> list[EmbedField]:
        return self._fields

    def add_field(
            self,
            name: str,
            value: str,
            *,
            inline: bool = True) -> Embed:
        """
        Add a field to the embed.

        Parameters
        ----------
        name : str
            The name of the field.
        value : str
            The value of the embed.
        inline : bool
            Whether or not the field should be inline.
        """

        self._fields.append(
            EmbedField(
                name=name,
                value=value,
                inline=inline,
            )
        )
        return self

    def remove_field(self, index: int) -> Embed:
        """
        Remove a field at a given index.

        Parameters
        ----------
        index : int
            The index of the field.
        """

        self._fields.pop(index)
        return self

    def insert_field_at(
            self,
            index: int,
            name: str,
            value: str,
            *,
            inline: bool = True) -> Embed:
        """
        Add a field to the embed at a specified location.

        Parameters
        ----------
        index : int
            The index that you want to add the field at.
        name : str
            The name of the field.
        value : str
            The value of the embed.
        inline : bool
            Whether or not the field should be inline.
        """

        self._fields.insert(
            index,
            EmbedField(
                name=name,
                value=value,
                inline=inline,
            )
        )
        return self

    def clear_fields(self) -> Embed:
        """
        Remove all of the fields from the embed.
        """

        self._fields.clear()
        return self


class MessageReference:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class Message:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class AllowedMentions:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class File:
    r"""
    A representation for an uploaded file to Discord.

    Parameters
    ----------
    data : bytes | str | pathlib.Path | io.IOBase
        The data that should be inserted into the file. Raw bytes can be
        provided (and is recommended), though a filename or `pathlib.Path`
        object can be used if you want the library to read the content directly,
        or a file handle can be provided directly.
    filename : str
        The filename given to the attachment. Any leading "SPOILER\_" names will
        be automatically removed.
    spoiler : bool
        Whether or not the file should be marked as a spoiler on send.

    Attributes
    ----------
    data : bytes
        The data associated with the attachment.
    filename : str
        The filename for the attachment.
    description : str | None
        The description of the file, if one is given.
    spoiler : bool
        Whether or not the attachment is a spoiler.
    content_type : str
        The type of the data.
    """

    __slots__ = (
        'data',
        'filename',
        'description',
        '_cs_content_type',
    )

    def __init__(
            self,
            data: bytes | str | pathlib.Path | io.IOBase,
            filename: str,
            *,
            description: str | None = None,
            spoiler: bool = False) -> None:
        self.data: bytes
        if isinstance(data, bytes):
            self.data = data
        elif isinstance(data, (str, pathlib.Path)):
            with open(data, 'rb') as a:
                self.data = a.read()
        elif isinstance(data, io.IOBase):
            pointer = data.tell()
            self.data = data.read()
            data.seek(pointer)
        else:
            raise ValueError("Unsupported type %s" % type(data))
        while filename.startswith("SPOILER_"):
            filename = filename[7:]
        self.filename: str = filename
        if spoiler:
            self.filename = f"SPOILER_{self.filename}"
        self.description: str | None = description

    @property
    def spoiler(self) -> bool:
        return self.filename.startswith("SPOILER_")

    @cached_slot_property("_cs_content_type")
    def content_type(self) -> str:
        try:
            content_type = get_mime_type_for_image(self.data[:16])
        except ValueError:
            if self.data.startswith(b'{'):
                content_type = 'application/json'
            else:
                content_type = 'application/octet-stream'
        return content_type

    def _to_data(self, id: int = 0) -> dict[str, Any]:
        v = {
            "id": id,
            "filename": self.filename,
            "description": self.description,
        }
        if self.description is None:
            v.pop("description")
        return v
