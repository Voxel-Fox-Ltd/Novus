import argparse
import asyncio
import logging
import sys
import typing
import os
import importlib
import io
import traceback

import discord
from discord.ext import commands
import toml

from .cogs.utils.database import DatabaseWrapper
from .cogs.utils.redis import RedisConnection
from .cogs.utils.statsd import StatsdConnection
from .cogs.utils.custom_bot import Bot
from .cogs.utils.custom_context import PrintContext
from .cogs.utils.shard_manager import ShardManagerServer


class CascadingLogger(logging.getLoggerClass()):
    """
    A logger class that changes all of the handlers loglevels as well.
    Stdout will change to the loglevel set, and stderr will change to the max of what's
    been specified and WARNING.
    """

    def setLevel(self, level):
        for i in self.handlers:
            if isinstance(i, logging.StreamHandler):
                if i.stream.name == "<stdout>":
                    i.setLevel(level)
                elif i.stream.name == "<stderr>":
                    i.setLevel(max([level, logging.WARNING]))
        super().setLevel(level)


logging.setLoggerClass(CascadingLogger)
logger = logging.getLogger('vbu')


def set_log_level(
        logger_to_change: typing.Union[logging.Logger, str],
        log_level: str,
        minimum_level: int = None) -> None:
    """
    Set a logger to a default log level.

    Parameters
    -----------
    logger_to_change: :class`logging.Logger`
        The logger you want to change.
    log_level: :class:`str`
        The log level that you want to set the logger to.

    Raises
    -------
    :class:`ValueError`
        An invalid log_level was passed to the method.
    """

    # Make sure we're setting it to something
    if log_level is None:
        return

    # Get the logger we want to change
    if isinstance(logger_to_change, str):
        logger_to_change = logging.getLogger(logger_to_change)

    # Get the log level
    try:
        level = getattr(logging, log_level.upper())
    except AttributeError:
        raise ValueError(f"The log level {log_level.upper()} wasn't found in the logging module")

    # Set the level
    if minimum_level is not None:
        logger_to_change.setLevel(max([level, minimum_level]))
    else:
        logger_to_change.setLevel(level)


def validate_sharding_information(args: argparse.Namespace) -> typing.Optional[typing.List[int]]:
    """
    Validate the given shard information and make sure that what's passed in is accurate.

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The parsed argparse namespace for the program.

    Returns
    --------
    List[:class:`int`]
        A list of shard IDs to use with the bot.
    """

    # Set up some short vars for us to use
    set_min_and_max = args.min is not None and args.max is not None
    set_shardcount = args.shardcount is not None

    # If we haven't said anything, assume one shard
    if not set_shardcount and not set_min_and_max:
        args.shardcount = 1
        return [0]

    # If we haven't set a min or max but we HAVE set a shardcount,
    # then assume we're using all shards
    if set_shardcount and not set_min_and_max:
        args.min = 0
        args.max = args.shardcount - 1

    # If we gave a min and max but no shardcount, that's just invalid
    if set_min_and_max and not set_shardcount:
        logger.critical("You set a min/max shard amount but no shard count")
        exit(1)

    # Work out the shard IDs to launch with
    shard_ids = list(range(args.min, args.max + 1))
    return shard_ids


class LogFilter(logging.Filter):
    """
    Filters (lets through) all messages with level < LEVEL.

    To make our log levels work properly, we need to set up a new filter for our stream handlers
    We're going to send most things to stdout, but a fair few sent over to stderr
    """

    # Props to these folks who I stole all this from
    # https://stackoverflow.com/a/28743317/2224197
    # https://stackoverflow.com/a/24956305/408556

    def __init__(self, filter_level: int):
        self.filter_level = filter_level

    def filter(self, record):
        # "<" instead of "<=": since logger.setLevel is inclusive, this should
        # be exclusive
        return record.levelno < self.filter_level


def _set_default_log_level(logger_name, log_filter, formatter, loglevel):
    logger = logging.getLogger(logger_name) if isinstance(logger_name, str) else logger_name

    set_log_level(logger, 'DEBUG')

    stdout_logger = logging.StreamHandler(sys.stdout)
    stdout_logger.addFilter(log_filter)
    stdout_logger.setFormatter(formatter)
    set_log_level(stdout_logger, loglevel)  # type: ignore
    logger.addHandler(stdout_logger)

    stderr_logger = logging.StreamHandler(sys.stderr)
    stderr_logger.setFormatter(formatter)
    set_log_level(stderr_logger, loglevel, logging.WARNING)  # type: ignore
    logger.addHandler(stderr_logger)


def create_subclassed_loggers():
    DatabaseWrapper.logger = logging.getLogger("vbu.database")
    RedisConnection.logger = logging.getLogger("vbu.redis")
    StatsdConnection.logger = logging.getLogger("vbu.statsd")


def set_default_log_levels(args: argparse.Namespace) -> None:
    """
    Set the default levels for the logger.

    Parameters
    -----------
    bot: :class:`voxelbotutils.Bot`
        The custom bot object containing the logger, database logger, and redis logger.
    args: :class:`argparse.Namespace`
        The argparse namespace saying what levels to set each logger to.
    """

    # formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(name)s] %(message)s')
    # formatter = logging.Formatter('{asctime} | {levelname: <8} | {module}:{funcName}:{lineno} - {message}', style='{')
    formatter = logging.Formatter('{asctime} | {levelname: <8} | {name}: {message}', style='{')
    log_filter = LogFilter(logging.WARNING)
    create_subclassed_loggers()
    loggers = [
        'vbu',
        'discord',
        'aiohttp',
        'aiohttp.access',
        'upgradechat',
    ]
    for i in loggers:
        if i is None:
            continue
        _set_default_log_level(i, log_filter, formatter, getattr(args, "loglevel", "ERROR"))


async def create_initial_database(db: DatabaseWrapper) -> bool:
    """
    Create the initial database using the internal database.psql file.
    """

    # Open the db file
    try:
        with open("./config/database.pgsql") as a:
            data = a.read()
    except Exception:
        return False

    # Get the statements
    create_table_statements = []
    current_line = ''
    for line in data.split('\n'):
        if line.lstrip().startswith('--'):
            continue
        current_line += line + '\n'
        if line.endswith(';') and not line.startswith(' '):
            create_table_statements.append(current_line.strip())
            current_line = ''

    # Let's do it baybeee
    for i in create_table_statements:
        if i and i.strip():
            await db(i.strip())

    # Sick we're done
    return True


async def start_database_pool(config: dict) -> None:
    """
    Start the database pool connection.
    """

    # Connect the database pool
    logger.info("Creating database pool")
    try:
        await DatabaseWrapper.create_pool(config['database'])
    except KeyError:
        raise Exception("KeyError creating database pool - is there a 'database' object in the config?")
    except ConnectionRefusedError:
        raise Exception(
            "ConnectionRefusedError creating database pool - did you set the right "
            "information in the config, and is the database running?"
        )
    except Exception:
        raise Exception("Error creating database pool")
    logger.info("Created database pool successfully")
    logger.info("Creating initial database tables")
    async with DatabaseWrapper() as db:
        await create_initial_database(db)


async def start_redis_pool(config: dict) -> None:
    """
    Start the redis pool connection.
    """

    # Connect the redis pool
    logger.info("Creating redis pool")
    try:
        await RedisConnection.create_pool(config['redis'])
    except KeyError:
        raise KeyError("KeyError creating redis pool - is there a 'redis' object in the config?")
    except ConnectionRefusedError:
        raise ConnectionRefusedError(
            "ConnectionRefusedError creating redis pool - did you set the right "
            "information in the config, and is the database running?"
        )
    except Exception:
        raise Exception("Error creating redis pool")
    logger.info("Created redis pool successfully")


class EventLoopCallbackHandler:
    """
    A callback handler for errors in the event loop so that they
    print to console properly, as well as sending to the event webhook
    if one is set up.

    Attributes
    -----------
    bot: :class:`voxelbotutils.Bot`
        The bot instance that the event loop is running.
    """

    bot: typing.Optional[Bot] = None

    @classmethod
    def callback(cls, future: asyncio.Future):
        # Print exceptions to console
        try:
            e = future.exception()
            if e is None:
                return
            raise e
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        except Exception as e:
            logger.error("Error in task was hit", exc_info=e)
            if cls.bot is None:
                return
            cls.bot.loop.create_task(cls.send_error_webhook(e))

    @classmethod
    async def send_error_webhook(cls, error: Exception):
        # Ping unhandled errors to the owners and to the event webhook
        error_string = "".join(traceback.format_exception(None, error, error.__traceback__))
        file_handle = io.StringIO(error_string + "\n")
        error_text = (
            f"Error `{error}` encountered.\nGuild `None`, channel `None`, "
            f"user `None`\n```\n[Task error]\n```"
        )

        # Assert some stuff
        try:
            assert cls.bot
            assert cls.bot.config
            assert cls.bot.user
        except AssertionError:
            return

        # DM to owners
        if cls.bot.config.get('dm_uncaught_errors', False):
            for owner_id in cls.bot.owner_ids:
                owner = cls.bot.get_user(owner_id) or await cls.bot.fetch_user(owner_id)
                file_handle.seek(0)
                file = discord.File(file_handle, filename="error_log.py")  # type: ignore
                await owner.send(error_text, file=file)

        # Ping to the webook
        event_webhook: typing.Optional[discord.Webhook] = cls.bot.get_event_webhook("unhandled_error")
        if not event_webhook:
            return
        try:
            avatar_url = str(cls.bot.user.display_avatar.url)
        except Exception:
            avatar_url = None
        try:
            username = cls.bot.user.name
        except Exception:
            username = cls.bot.application_id
            if username is None:
                username = cls.bot.config.get("oauth", {}).get("client_id", None) or "Application ID not found"
        if event_webhook:
            file_handle.seek(0)
            try:
                file = discord.File(file_handle, filename="error_log.py")
                await event_webhook.send(
                    error_text,
                    file=file,
                    username=f"{username} - Error",
                    avatar_url=avatar_url,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            except discord.HTTPException as e:
                cls.bot.logger.error(f"Failed to send webhook for event unhandled_error - {e}")


def set_event_loop():
    """
    Set up the event loop policy to use for asyncio, and set up
    a callback handler to log exceptions.
    """

    # Set up uvloop if we're on Linux
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    # If we're on Windows, set up a different event loop policy
    if sys.platform.startswith('win32'):
        if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        else:
            asyncio.set_event_loop(asyncio.ProactorEventLoop())

    # Set up the task factory
    def task_factory(loop: asyncio.AbstractEventLoop, coro) -> asyncio.Task:
        t = asyncio.Task(coro, loop=loop)
        t.add_done_callback(EventLoopCallbackHandler.callback)
        return t

    # And add it to our loop
    loop = asyncio.get_event_loop()
    loop.set_task_factory(task_factory)


async def run_bot(args: argparse.Namespace) -> None:
    """
    Starts the bot, connects the database, runs the async loop forever.

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The arguments namespace that wants to be run.
    """

    os.chdir(args.bot_directory)
    set_event_loop()

    # And run file
    shard_ids = validate_sharding_information(args)
    bot = Bot(
        shard_count=args.shardcount,
        shard_ids=shard_ids,
        config_file=args.config_file,
    )
    EventLoopCallbackHandler.bot = bot

    # Set up loggers
    bot.logger = logger.getChild("bot")
    set_default_log_levels(args)

    # Connect the database pool
    if bot.config.get('database', {}).get('enabled', False):
        await start_database_pool(bot.config)  # type: ignore

    # Connect the redis pool
    if bot.config.get('redis', {}).get('enabled', False):
        await start_redis_pool(bot.config)  # type: ignore

    # Load the bot's extensions
    logger.info('Loading extensions... ')
    bot.load_all_extensions()

    # Run the bot
    try:
        logger.info("Running bot")
        await bot.start(run_startup_method=not args.no_startup)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Logging out bot")
        await bot.close()

    # We're now done running the bot, time to clean up and close
    if bot.config.get('database', {}).get('enabled', False):
        logger.info("Closing database pool")
        try:
            if DatabaseWrapper.pool:
                await asyncio.wait_for(DatabaseWrapper.pool.close(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.error("Couldn't gracefully close the database connection pool within 30 seconds")
    if bot.config.get('redis', {}).get('enabled', False):
        logger.info("Closing redis pool")
        RedisConnection.pool.close()


async def run_interactions(args: argparse.Namespace) -> None:
    """
    Starts the bot, connects the database, runs the async loop forever.

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The arguments namespace that wants to be run.
    """

    from aiohttp.web import Application, AppRunner, TCPSite
    os.chdir(args.bot_directory)
    set_event_loop()

    # And run file
    bot = Bot(config_file=args.config_file, intents=discord.Intents.none())
    bot.is_interactions_only = True
    EventLoopCallbackHandler.bot = bot

    # Set up loggers
    bot.logger = logger.getChild("bot")
    set_default_log_levels(args)

    # Connect the database pool
    if bot.config.get('database', {}).get('enabled', False):
        await start_database_pool(bot.config)

    # Connect the redis pool
    if bot.config.get('redis', {}).get('enabled', False):
        await start_redis_pool(bot.config)

    # Load the bot's extensions
    logger.info('Loading extensions... ')
    bot.load_all_extensions()

    # Run the bot
    logger.info("Logging in bot")
    await bot.login()
    if args.connect:
        logger.info("Connecting bot to gateway")
        await bot.connect()

    # Run the startup task
    logger.info("Running bot startup task")
    bot.startup_method = bot.loop.create_task(bot.startup())

    # Create the webserver
    app = Application(loop=asyncio.get_event_loop(), debug=args.debug)
    app.router.add_routes(
        commands.get_interaction_route_table(
            bot,
            bot.config.get("pubkey", ""),
            path=args.path,
        )
    )

    # Start the HTTP server
    logger.info("Creating webserver...")
    application = AppRunner(app)
    await application.setup()
    webserver = TCPSite(application, host=args.host, port=args.port)

    # Start the webserver
    await webserver.start()
    host = args.host if args.host != '0.0.0.0' else 'localhost'
    logger.info(f"Server started - http://{host}:{args.port}/")

    # This is the forever loop
    try:
        logger.info("Running webserver")
        while True:
            await asyncio.sleep(0.1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Stopping webserver")

    # We're now done running the webserver, time to clean up and close
    if bot.config.get('database', {}).get('enabled', False):
        logger.info("Closing database pool")
        try:
            if DatabaseWrapper.pool:
                await asyncio.wait_for(DatabaseWrapper.pool.close(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.error("Couldn't gracefully close the database connection pool within 30 seconds")
    if bot.config.get('redis', {}).get('enabled', False):
        logger.info("Closing redis pool")
        RedisConnection.pool.close()


async def run_website(args: argparse.Namespace) -> None:
    """
    Starts the website, connects the database, logs in the specified bots,
    runs the async loop forever.

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The arguments namespace that wants to be run.
    """

    # Load our imports here so we don't need to require them all the time
    from aiohttp.web import Application, AppRunner, TCPSite
    from aiohttp_jinja2 import setup as jinja_setup
    from aiohttp_session import setup as session_setup, SimpleCookieStorage
    from aiohttp_session.cookie_storage import EncryptedCookieStorage as ECS
    from jinja2 import FileSystemLoader
    import re
    import html
    from datetime import datetime as dt
    import markdown

    os.chdir(args.website_directory)
    set_event_loop()

    # Read config
    with open(args.config_file) as a:
        config = toml.load(a)

    # Create website object - don't start based on argv
    app = Application(debug=args.debug)
    app['static_root_url'] = '/static'
    for route in config['routes']:
        module = importlib.import_module(f"website.{route.replace('/', '.')}", "temp")
        app.router.add_routes(module.routes)
    app.router.add_static('/static', os.getcwd() + '/website/static', append_version=True)

    # Add middlewares
    if args.debug:
        session_setup(app, SimpleCookieStorage(max_age=1_000_000))
    else:
        config_key: str | None = config.get("cookie_encryption_key")
        if config_key:
            key = config_key.encode()
        else:
            key = os.urandom(32)
        session_setup(app, ECS(key, max_age=1_000_000))
    jinja_env = jinja_setup(app, loader=FileSystemLoader(os.getcwd() + '/website/templates'))

    # Add our jinja env filters
    def regex_replace(string, find, replace):
        return re.sub(find, replace, string, re.IGNORECASE | re.MULTILINE)

    def escape_text(string):
        return html.escape(string)

    def timestamp(string):
        return dt.fromtimestamp(float(string))

    def int_to_hex(string):
        return format(hex(int(string))[2:], "0>6")

    def to_markdown(string):
        return markdown.markdown(string, extensions=['extra'])

    def display_mentions(string, users):
        def get_display_name(group):
            user = users.get(group.group('userid'))
            if not user:
                return 'unknown-user'
            return user.get('display_name') or user.get('username')
        return re.sub(
            '(?:<|(?:&lt;))@!?(?P<userid>\\d{16,23})(?:>|(?:&gt;))',
            lambda g: f'<span class="chatlog__mention">@{get_display_name(g)}</span>',
            string,
            re.IGNORECASE | re.MULTILINE,
        )

    def display_emojis(string):
        def get_html(group):
            return (
                f'<img class="discord_emoji" src="https://cdn.discordapp.com/emojis/{group.group("id")}'
                f'.{"gif" if group.group("animated") else "png"}" alt="Discord custom emoji: '
                f'{group.group("name")}" style="height: 1em; width: auto;">'
            )
        return re.sub(
            r"(?P<emoji>(?:<|&lt;)(?P<animated>a)?:(?P<name>\w+):(?P<id>\d+)(?:>|&gt;))",
            get_html,
            string,
            re.IGNORECASE | re.MULTILINE,
        )

    jinja_env.filters['regex_replace'] = regex_replace
    jinja_env.filters['escape_text'] = escape_text
    jinja_env.filters['timestamp'] = timestamp
    jinja_env.filters['int_to_hex'] = int_to_hex
    jinja_env.filters['markdown'] = to_markdown
    jinja_env.filters['display_mentions'] = display_mentions
    jinja_env.filters['display_emojis'] = display_emojis

    # Add our connections and their loggers
    app['database'] = DatabaseWrapper
    app['redis'] = RedisConnection
    app['logger'] = logger.getChild("route")
    app['stats'] = StatsdConnection

    # Add our config
    app['config'] = config

    # Set log levels
    set_default_log_levels(args)

    # Connect the database pool
    if app['config'].get('database', {}).get('enabled', False):
        await start_database_pool(app['config'])

    # Connect the redis pool
    if app['config'].get('redis', {}).get('enabled', False):
        await start_redis_pool(app['config'])

    # Add our bots
    app['bots'] = {}
    for index, (bot_name, bot_config_location) in enumerate(config.get('discord_bot_configs', dict()).items()):
        bot = Bot(f"./config/{bot_config_location}")
        app['bots'][bot_name] = bot
        try:
            await bot.login()
            bot.load_all_extensions()
        except Exception:
            logger.error(f"Failed to start bot {bot_name}", exc_info=True)
            exit(1)

    # Start the HTTP server
    logger.info("Creating webserver...")
    application = AppRunner(app)
    await application.setup()
    webserver = TCPSite(application, host=args.host, port=args.port)

    # Start the webserver
    await webserver.start()
    host = args.host if args.host != '0.0.0.0' else 'localhost'
    logger.info(f"Server started - http://{host}:{args.port}/")

    # This is the forever loop
    try:
        logger.info("Running webserver")
        while True:
            await asyncio.sleep(0.1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Stopping webserver")

    # We're now done running the bot, time to clean up and close
    logger.info("Running application cleanup")
    await application.cleanup()
    logger.info("Running application shutdown")
    await application.shutdown()

    # Close db and redis
    if config.get('database', {}).get('enabled', False):
        logger.info("Closing database pool")
        try:
            if DatabaseWrapper.pool:
                await asyncio.wait_for(DatabaseWrapper.pool.close(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.error("Couldn't gracefully close the database connection pool within 30 seconds")
    if config.get('redis', {}).get('enabled', False):
        logger.info("Closing redis pool")
        RedisConnection.pool.close()


async def run_sharder(args: argparse.Namespace) -> None:
    """
    Starts the sharder, connects the redis, runs the async loop forever.

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The arguments namespace that wants to be run.
    """

    set_event_loop()
    set_default_log_levels(args)

    # Run the bot
    logger.info(f"Running sharder with {args.concurrency} shards")
    await ShardManagerServer(args.host, args.port, args.concurrency).run()
    try:
        while True:
            await asyncio.sleep(0.1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Logging out sharder")


async def run_shell(args: argparse.Namespace) -> None:
    """
    Starts the shell for you.

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The arguments namespace that wants to be run.
    """

    os.chdir(args.bot_directory)
    set_event_loop()

    # And run file
    bot = Bot(config_file=args.config_file)

    # Set up loggers
    bot.logger = logger.getChild("bot")
    set_default_log_levels(args)

    # Connect the database pool
    if bot.config.get('database', {}).get('enabled', False):
        await start_database_pool(bot.config)

    # Connect the redis pool
    if bot.config.get('redis', {}).get('enabled', False):
        await start_redis_pool(bot.config)

    # Load the bot's extensions
    logger.info('Loading extensions... ')
    bot.load_all_extensions()

    # Set up the default env
    import voxelbotutils as vbu
    import discord
    from discord.ext import commands
    import textwrap
    import traceback
    import re
    env = {
        'bot': bot,
        'vbu': vbu,
        'discord': discord,
        'commands': commands,
        'ctx': PrintContext(bot),
    }

    # Run the bot
    try:
        logger.info("Running bot")
        await bot.login()

        # Run our shell loop
        while True:

            # Get a user input
            line = input(">>> ")
            if not line.strip():
                line = "None"

            # See if they want to save that to a var
            var_name = None
            if (match := re.search(r"^([a-zA-Z_][a-zA-Z0-9_\.]*) ?=", line)):
                var_name = match.group(1)
                line = line.replace(match.group(0), "").lstrip()
            elif (match := re.search(r"^(?:from (?:[a-zA-Z_][a-zA-Z0-9_]*) )?import ([a-zA-Z_][a-zA-Z0-9_]*)", line)):
                var_name = match.group(1)
                line = line + f"\nreturn {var_name}"

            # Make sure that something is returned
            if not line.split("\n")[-1].startswith("return "):
                line = "return " + line

            # Make it asyncable
            code = f'async def _func():\n{textwrap.indent(line, "  ")}'

            # Run the function
            try:
                exec(code, env)
                func = env['_func']
                try:
                    ret = await func()

                # Catch any errors
                except Exception:
                    print(traceback.format_exc().rstrip())

                # Deal with the result
                else:
                    if var_name is not None:
                        env.update({var_name: ret})
                    elif ret is not None:
                        print(repr(ret))
            except Exception:
                print(traceback.format_exc().rstrip())

    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Logging out bot")
        await bot.close()

    # We're now done running the bot, time to clean up and close
    if bot.config.get('database', {}).get('enabled', False):
        logger.info("Closing database pool")
        try:
            if DatabaseWrapper.pool:
                await asyncio.wait_for(DatabaseWrapper.pool.close(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.error("Couldn't gracefully close the database connection pool within 30 seconds")
    if bot.config.get('redis', {}).get('enabled', False):
        logger.info("Closing redis pool")
        RedisConnection.pool.close()


async def run_modify_commands(args: argparse.Namespace) -> None:
    """
    Modifies the commands available for the slash command instance

    Parameters
    -----------
    args: :class:`argparse.Namespace`
        The arguments namespace that wants to be run.
    """

    os.chdir(args.bot_directory)
    set_event_loop()

    # And run file
    bot = Bot(config_file=args.config_file)

    # Set up loggers
    bot.logger = logger.getChild("bot")
    set_default_log_levels(args)

    # Load the bot's extensions
    logger.info('Loading extensions... ')
    bot.load_all_extensions()

    # Run the bot
    logger.info("Running bot")
    await bot.login()

    # Perform our action
    ctx = PrintContext(bot)
    if args.action == "add":
        command = bot.get_command("addapplicationcommands")
        assert command is not None
        ctx.command = command
        coro = ctx.invoke(ctx.command, args.guild)  # type: ignore
    else:
        command = bot.get_command("removeapplicationcommands")
        assert command is not None
        ctx.command = command
        coro = ctx.invoke(ctx.command, args.guild)  # type: ignore
    await coro

    # Logout the bot
    logger.info("Logging out bot")
    await bot.close()
