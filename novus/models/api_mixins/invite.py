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

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ..invite import Invite

__all__ = (
    'InviteAPIMixin',
)


class InviteAPIMixin:

    id: int
    _state: HTTPConnection
    INVITE_LINK_REGEX = re.compile(r"(?:https?://)?discord\.gg/(?P<code>[a-zA-Z0-9]+)")

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            code: str) -> Invite:
        """
        Get an invite object via its code.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        code : str
            The invite code.

        Returns
        -------
        novus.Invite
            The invite associated with the code.
        """

        # Try and parse a URL
        if "/" in code:
            match = cls.INVITE_LINK_REGEX.search(code)
            if match is not None:
                code = match.group("code")
            else:
                pass  # Could raise here, but I'd rather the API at this point

        # API request
        return await state.invite.get_invite(code)

    async def delete(
            self: Invite,  # pyright: ignore
            *,
            reason: str | None = None) -> Invite:
        """
        Delete an instance of the invite.

        .. note::

            This is one of the few API mixin methods that can't outright take
            a `StateSnowflake` for its `self` as the delete method requires
            a ``.code`` attribute. You can still do this by adding a ``code``
            attribute to an `Object`, you'd just be unable to do this via the
            constructor.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Invite
            The deleted invite object.
        """

        return await self._state.invite.delete_invite(self.code, reason=reason)
