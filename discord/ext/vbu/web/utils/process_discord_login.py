import asyncio
from urllib.parse import urlencode
from datetime import datetime as dt, timedelta
import typing

import aiohttp
import aiohttp_session
from aiohttp.web import HTTPFound, Request, json_response
import yarl

from .get_avatar_url import get_avatar_url
from .oauth_models import OauthMember


def get_discord_login_url(request: Request, redirect_uri: str = None) -> str:
    """
    Returns a login URL for your website based on the oauth information given in
    your :class:`website config<WebsiteConfig.oauth>`.

    Args:
        request (Request): The request from which this command call is coming from.
        redirect_uri (str, optional): Where the user should be redirected to after pressing authorize.
        oauth_scopes (list, optional): The scopes that the login URL will ask for. Does not necessarily mean we'll get them.

    Returns:
        str: The login URL that we want to use.
    """

    config = request.app['config']
    oauth_data = config['oauth']
    oauth_scopes = config['oauth_scopes']
    parameters = {
        'response_type': 'code',
        'client_id': oauth_data['client_id'],
    }
    if redirect_uri:
        if 'http' not in redirect_uri:
            redirect_uri = config['website_base_url'].rstrip('/') + '/' + redirect_uri.lstrip('/')
        parameters['redirect_uri'] = redirect_uri
    if oauth_scopes:
        parameters['scope'] = ' '.join(oauth_scopes)
    return 'https://discordapp.com/api/v6/oauth2/authorize?' + urlencode(parameters)


async def process_discord_login(request: Request) -> None:
    """
    Process a Discord login and store the information in the provided session based off
    of a callback from your Discord redirect URI.

    Args:
        request (Request): The request from which this command call is coming from.
        oauth_scopes (list): The list of oauth scopes that we asked for.
    """

    # Get the code
    code = request.query.get('code')
    if not code:
        return HTTPFound(location='/')

    # Get the bot
    config = request.app['config']
    oauth_data = config['oauth']
    oauth_scopes = config['oauth_scopes']

    # Generate the post data
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'scope': ' '.join(oauth_scopes),
        **oauth_data,
    }

    base_url = yarl.URL(config['website_base_url'])
    if base_url.explicit_port:
        data['redirect_uri'] = "{0.scheme}://{0.host}:{0.port}{1.path}".format(base_url, request.url)
    else:
        data['redirect_uri'] = "{0.scheme}://{0.host}{1.path}".format(base_url, request.url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make session so we can do stuff with it
    session_storage = await aiohttp_session.get_session(request)

    # Make the request
    async with aiohttp.ClientSession(loop=request.loop) as session:

        # Get auth
        token_url = "https://discordapp.com/api/v6/oauth2/token"
        async with session.post(token_url, data=data, headers=headers) as r:
            token_info = await r.json()
        if token_info.get('error'):
            token_info['redirect_uri'] = data['redirect_uri']
            session_storage['login_error'] = token_info
            return json_response(token_info)  # Error getting the token, just ignore it

        # Update headers
        headers.update({
            "Authorization": f"Bearer {token_info['access_token']}"
        })
        token_info['expires_at'] = (dt.utcnow() + timedelta(seconds=token_info['expires_in'])).timestamp()
        updated_token_info = session_storage.get('token_info', dict())
        updated_token_info.update(token_info)
        session_storage['token_info'] = updated_token_info

    # Get user
    if "identify" in oauth_scopes:
        await get_user_info_from_session(request, refresh=True)


async def get_user_info_from_session(request: Request, *, refresh: bool = False):
    """
    Get the user's info.
    """

    session_storage = await aiohttp_session.get_session(request)
    if refresh is False:
        return session_storage['user_info']
    user_url = "https://discordapp.com/api/v6/users/@me"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    headers.update({
        "Authorization": f"Bearer {session_storage['token_info']['access_token']}"
    })
    async with aiohttp.ClientSession(loop=request.loop) as session:
        async with session.get(user_url, headers=headers) as r:
            user_info = await r.json()
    user_info['avatar_url'] = get_avatar_url(user_info)
    session_storage['user_info'] = user_info
    session_storage['user_id'] = int(user_info['id'])
    session_storage['logged_in'] = True
    return user_info


async def get_access_token_from_session(
        request: Request, *, refresh_if_expired: bool = True,
        refresh: bool = False) -> str:
    """
    Get the access token for a given user.
    """

    # Get relevant data
    session_storage = await aiohttp_session.get_session(request)
    config = request.app['config']
    oauth_data = config['oauth']
    oauth_scopes = config['oauth_scopes']

    # See if we even need to make a new request
    if refresh:
        pass
    elif refresh_if_expired is False or session_storage['token_info']['expires_at'] < dt.utcnow().timestamp():
        return session_storage['token_info']['access_token']

    # Generate the post data
    data = {
        'grant_type': 'refresh_token',
        'scope': ' '.join(oauth_scopes or session_storage['token_info']['scope']),
        **oauth_data,
    }
    if request.url.explicit_port:
        data['redirect_uri'] = "http://{0.host}:{0.port}{0.path}".format(request.url)
    else:
        data['redirect_uri'] = "https://{0.host}{0.path}".format(request.url)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the request
    async with aiohttp.ClientSession(loop=request.loop) as session:

        # Get auth
        token_url = "https://discordapp.com/api/v6/oauth2/token"
        async with session.post(token_url, data=data, headers=headers) as r:
            token_info = await r.json()
        if token_info.get('error'):
            return ""  # Error getting the token, just ignore it, TODO raise something

    # Store data
    token_info['expires_at'] = (dt.utcnow() + timedelta(seconds=token_info['expires_in'])).timestamp()
    updated_token_info = session_storage['token_info']
    updated_token_info.update(token_info)
    session_storage['token_info'] = updated_token_info
    return updated_token_info['access_token']


async def get_user_guilds_from_session(request: Request, bot_key: str = "bot") -> typing.List[OauthMember]:
    """
    Returns a list of guilds that the user is in based on the request's logged in user.
    """

    # Get auth
    session_storage = await aiohttp_session.get_session(request)
    token_info = session_storage['token_info']
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {token_info["access_token"]}'
    }

    # Make the request
    async with aiohttp.ClientSession(loop=request.loop) as session:
        guilds_url = "https://discordapp.com/api/v6/users/@me/guilds"

        # Loop until success
        async with session.get(guilds_url, headers=headers) as r:
            guild_info = await r.json()
            if not r.ok:
                return []  # Missing permissions or server error

    # Return guild info
    bot = request.app['bots'].get(bot_key)
    return [OauthMember(bot, i, session_storage['user_info']) for i in guild_info]


async def add_user_to_guild_from_session(request: Request, bot_index: str, guild_id: int) -> bool:
    """
    Adds the user to the given guild (if the correct scopes were previously provided).
    Returns a boolean of whether or not that user was added (or was already in the guild) successfully.
    """

    # Get the bot
    session_storage = await aiohttp_session.get_session(request)
    user_info = session_storage['user_info']

    # Get our headers
    guild_join_url = f"https://discordapp.com/api/v6/guilds/{guild_id}/members/{user_info['id']}"
    headers = {
        'Authorization': f"Bot {request.app['config']['discord_bots'][bot_index]}"
    }

    # Get our access token
    data = {
        'access_token': await get_access_token_from_session(request)
    }

    # Make the request
    async with aiohttp.ClientSession(loop=request.loop) as session:
        async with session.put(guild_join_url, headers=headers, json=data) as r:
            return str(r.status)[0] == '2'  # 201 - Added; 204 - Already in the guild
