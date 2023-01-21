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

from typing import TYPE_CHECKING

from vfflags import Flags

__all__ = (
    'UserFlags',
)


class UserFlags(Flags):

    if TYPE_CHECKING:

        def __init__(self, value: int = 0, **kwargs):
            ...

        staff: bool
        partner: bool
        hypesquad: bool
        bug_hunter_level_1: bool
        hypesquad_house_bravery: bool
        hypesquad_house_brilliance: bool
        hypesquad_house_balance: bool
        premium_early_supporter: bool
        team_pseudo_user: bool
        bug_hunter_level_2: bool
        verified_bot: bool
        verified_developer: bool
        certified_moderator: bool
        bot_http_interactions: bool
        active_developer: bool

    CREATE_FLAGS = {
        "staff": 1 << 0,
        "partner": 1 << 1,
        "hypesquad": 1 << 2,
        "bug_hunter_level_1": 1 << 3,
        "hypesquad_house_bravery": 1 << 6,
        "hypesquad_house_brilliance": 1 << 7,
        "hypesquad_house_balance": 1 << 8,
        "premium_early_supporter": 1 << 9,
        "team_pseudo_user": 1 << 10,
        "bug_hunter_level_2": 1 << 14,
        "verified_bot": 1 << 16,
        "verified_developer": 1 << 17,
        "certified_moderator": 1 << 18,
        "bot_http_interactions": 1 << 19,
        "active_developer": 1 << 22,
    }
