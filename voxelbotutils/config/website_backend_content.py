from aiohttp.web import HTTPFound, Request, Response, RouteTableDef
import aiohttp_session
from discord.ext import vbu


routes = RouteTableDef()


@routes.get("/login_processor")
async def login_processor(request: Request):
    """
    Page the discord login redirects the user to when successfully logged in with Discord.
    """

    # Process their login code
    v = await vbu.web.process_discord_login(request)

    # It failed - we want to redirect back to the index
    if isinstance(v, Response):
        return HTTPFound(location="/")

    # It succeeded - let's redirect them to where we specified to go if we
    # used a decorator, OR back to the index page
    session = await aiohttp_session.get_session(request)
    return HTTPFound(location=session.pop("redirect_on_login", "/"))


@routes.get("/logout")
async def logout(request: Request):
    """
    Destroy the user's login session.
    """

    session = await aiohttp_session.get_session(request)
    session.invalidate()
    return HTTPFound(location="/")


@routes.get("/login")
async def login(request: Request):
    """
    Redirect the user to the bot's Oauth login page.
    """

    return HTTPFound(location=vbu.web.get_discord_login_url(request, "/login_processor"))
