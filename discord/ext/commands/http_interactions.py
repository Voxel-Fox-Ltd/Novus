"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import typing
import logging
import asyncio
import time

from aiohttp import web
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from .bot import BotBase
from discord.interactions import Interaction, HTTPInteractionResponse, InteractionType

if typing.TYPE_CHECKING:
    from discord.types.interactions import Interaction as InteractionPayload


__all__ = (
    'get_interaction_route_table',
)


log = logging.getLogger("discord.interactions")
SLEEP_TIME = 2.7


def get_invalid_response(*, status: int = 401, reason: str = "Invalid request signature") -> web.StreamResponse:
    return web.StreamResponse(status=status, reason=reason)


async def verify_headers(request: web.Request, application_public_key: str) -> typing.Optional[web.StreamResponse]:
    """
    Verify whether the headers of a given Discord response both
    *exist* and are valid.

    Stolen neatly from the Discord API docs.
    """

    verify_key = VerifyKey(bytes.fromhex(application_public_key))

    signature = request.headers.get("X-Signature-Ed25519")
    if not signature:
        log.debug("Received interaction without a signature header")
        return get_invalid_response()
    timestamp = request.headers.get("X-Signature-Timestamp")
    if not timestamp:
        log.debug("Received interaction without a timestamp header")
        return get_invalid_response()
    body_bytes = await request.read()
    body = body_bytes.decode()

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        log.debug("Received interaction with valid signature")
    except BadSignatureError:
        log.debug("Received interaction an invalid signature")
        return get_invalid_response()
    return None


def get_interaction_route_table(bot: BotBase, application_public_key: str, *, path: str = "/interactions"):
    """
    Get an interactions endpoint that works with aiohttp. This method
    only works with logged in bots, as it uses the bot's HTTP client.

    .. versionadded:: 0.0.3

    Parameters
    -----------
    bot: :class:`discord.ext.commands.Bot`
        The bot instance that the command should be passed into.
    application_public_key: :class:`str`
        The application's public key, which is used to verify the headers.
    path: :class:`str`
        The path that the route should be added as. Defaults to ``/interactions``.
    """

    routes = web.RouteTableDef()

    @routes.post(path)
    async def wrapper(request: web.Request) -> web.StreamResponse:
        """
        Handle an actual response from Discord.
        """

        # Verify the request headers
        if (response := await verify_headers(request, application_public_key)) is not None:
            return response

        # Grab the data
        try:
            data: typing.Optional[InteractionPayload] = await request.json()
        except Exception:
            data = None
        if data is None:
            return get_invalid_response(status=400, reason="Invalid request")
        log.debug("Interaction data received - %s", data)

        # Grab the interaction
        interaction: Interaction = Interaction(data=data, state=bot._connection)
        interaction._cs_response = HTTPInteractionResponse(request, interaction)

        # Respond
        if interaction.type == InteractionType.ping:
            await interaction.response.pong()
        elif interaction.type == InteractionType.application_command:
            bot.dispatch('slash_command', interaction)
        elif interaction.type == InteractionType.autocomplete:
            bot.dispatch('autocomplete_interaction', interaction)
        elif interaction.type == InteractionType.component:
            bot.dispatch('component_interaction', interaction)
        elif interaction.type == InteractionType.modal_submit:
            bot.dispatch('modal_submit', interaction)
        bot.dispatch("interaction", interaction)

        # Sleep for a couple seconds, just so we don't try and return without
        # sending a response from inside the bot
        assert isinstance(interaction.response, HTTPInteractionResponse)
        t0 = time.time()
        while interaction.response._aiohttp_response._eof_sent is False and time.time() - t0 < SLEEP_TIME:
            await asyncio.sleep(0.01)

        # And give some return data
        return interaction.response._aiohttp_response

    @routes.get(path)
    async def get_wrapper(request: web.Request) -> web.StreamResponse:
        """
        Handle a GET request from the browser.
        """

        return web.Response(text=f"{bot.user or 'Running interaction server'!s}")

    return routes
