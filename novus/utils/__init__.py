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

from .cached_slots import *
from .enums import *
from .files import *
from .missing import *
from .repr import *
from .snowflakes import *
from .times import *

__all__: tuple[str, ...] = (
    'DiscordDatetime',
    'ME',
    'MISSING',
    'add_not_missing',
    'bytes_to_base64_data',
    'cached_slot_property',
    'generate_repr',
    'get_mime_type_for_image',
    'parse_timestamp',
    'try_enum',
    'try_id',
    'try_object',
    'try_snowflake',
)
