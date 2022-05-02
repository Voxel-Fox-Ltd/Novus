import functools

import aiohttp_session
from aiohttp.web import HTTPFound, Request


def add_discord_arguments(
        *, redirect_if_logged_out: str = None,
        redirect_if_logged_in: str = None):
    """
    This function is a wrapper around all routes. It takes the output and
    adds the user info and request to the returning dictionary
    It must be applied before the template decorator.

    Args:
        redirect_if_logged_out (str, optional): A location to direct the user
            to should they be logged out.
        redirect_if_logged_in (str, optional): A location to direct the user
            to if they are logged in already.
    """

    def inner_wrapper(func):
        """
        An inner wrapper so I can get args at the outer level.
        """

        @functools.wraps(func)
        async def wrapper(request:Request):
            """
            This is the wrapper that does all the heavy lifting.
            """

            # Run function
            data = await func(request)

            # See if we're returning to a redirect
            if isinstance(data, HTTPFound):

                # If we're telling them to login
                if data.location == request.app['config']['login_url']:
                    session = await aiohttp_session.get_session(request)

                    # We can send them back to where they tried to go initially
                    if 'redirect_on_login' not in session:
                        session['redirect_on_login'] = str(request.url)

            # It's not a redirect and it isn't data, I'll just leave it alone
            if not isinstance(data, dict):
                return data

            # See if we need to take them to a new place (already logged in)
            session = await aiohttp_session.get_session(request)
            login_redirect = session.pop('redirect_on_login', None)
            if login_redirect:
                return HTTPFound(location=login_redirect)

            # Update jinja params
            if data is None:
                data = dict()
            data.update({'session': session})
            if 'user_info' not in data:
                try:
                    data.update({'user_info': session['user_info']})
                except KeyError:
                    data.update({'user_info': None})
            if 'request' not in data:
                data.update({'request': request})

            # Check return relevant info
            if redirect_if_logged_out and session.get('user_id') is None:
                return HTTPFound(location=redirect_if_logged_out)
            elif redirect_if_logged_in and session.get('user_id') is not None:
                return HTTPFound(location=redirect_if_logged_in)

            return data
        return wrapper
    return inner_wrapper
