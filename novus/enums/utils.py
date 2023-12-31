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

from typing import Any

from enum import Enum as E
from enum import EnumMeta as EM

__all__ = (
    'Enum',
)


class EnumMeta(EM):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.__doc__:
            self.__doc__ += "\n\n"
        else:
            self.__doc__ = ""
        if "Attributes\n------" in self.__doc__:
            return
        self.__doc__ = "Attributes\n---------"
        for attr in dir(self):
            if attr.startswith("_"):
                continue
            self.__doc__ += "\n" + attr


class Enum(E, metaclass=EnumMeta):

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}.{self.name}'
