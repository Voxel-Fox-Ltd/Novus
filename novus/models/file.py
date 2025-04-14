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

import io
import pathlib
from typing import Any

from ..utils import cached_slot_property, get_mime_type_for_image

__all__ = (
    'File',
)


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
        elif isinstance(data, io.IOBase):  # pyright: ignore[reportUnnecessaryIsInstance]
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
