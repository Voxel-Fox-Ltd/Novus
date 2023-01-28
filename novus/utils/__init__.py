# flake8: noqa

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

from typing import Any, Literal

from .snowflakes import *
from .repr import *
from .files import *
from .cached_slots import *
from .times import *
from .enums import *


class MissingObject:

    __slots__ = ()

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> Literal['MISSING']:
        return 'MISSING'


MISSING: Any = MissingObject()
