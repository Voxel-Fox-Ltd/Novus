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


"""
The payloads subpackage contains the payload classes for each payload type
from Discord. These will mostly be used to type hint payloads, and won't be
super helpful internally in the library.

Of note here: snowflakes (IDs) will be documented as strings as thats's what
the Discord API returns. This is regardless of the fact that the library treats
them as integers.
"""
