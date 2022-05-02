import functools

import aiohttp_session
from aiohttp.web import HTTPFound, Request


async def is_logged_in(request: Request):
    """
    Returns whether or not the user for the given request is logged in.
    """

    session = await aiohttp_session.get_session(request)
    if session.new or session.get('logged_in', False) is False:
        return False
    return True


def requires_login():
    """
    Using this wrapper on a route means that the user needs to be logged in to see the page.
    If they're not logged in then they'll be redirected to the login URL as set in your
    :attr:`website config<WebsiteConfig.login_url>`.
    """

    def inner_wrapper(func):
        """An inner wrapper so I can get args at the outer level"""

        @functools.wraps(func)
        async def wrapper(request: Request):
            """This is the wrapper that does all the heavy lifting"""

            # See if we have token info
            session = await aiohttp_session.get_session(request)
            if session.new or session.get('logged_in', False) is False:
                before = session.get('redirect_on_login')
                session['redirect_on_login'] = before or str(request.url)
                root_url = request.app['config']['login_url'].rstrip('/').split('//')[-1]
                if request.app['config']['login_url'] in str(request.url):
                    session['redirect_on_login'] = '/'
                return HTTPFound(location=request.app['config']['login_url'])

            # We're already logged in
            return await func(request)

        return wrapper
    return inner_wrapper
