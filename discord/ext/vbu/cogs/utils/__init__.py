import re as _re

from . import checks, converters, errors, menus, types
from .context_embed import Embed
from .custom_bot import MinimalBot, Bot
from .custom_cog import Cog
from .custom_context import Context, AbstractMentionable, PrintContext, SlashContext
from .database import DatabaseWrapper, DatabaseTransaction
from .redis import RedisConnection, RedisChannelHandler, redis_channel_handler
from .statsd import StatsdConnection
from .time_value import TimeValue
from .paginator import Paginator
from .help_command import HelpCommand
from .string import Formatter
from .component_check import component_check, component_id_check
from .embeddify import Embeddify
from .twitch_stream import TwitchStream
from .translation import translation, i18n


__all__ = (
    'checks',
    'converters',
    'errors',
    'menus',
    'types',
    'Embed',
    'MinimalBot',
    'Bot',
    'Cog',
    'Context',
    'AbstractMentionable',
    'PrintContext',
    'SlashContext',
    'DatabaseWrapper',
    'DatabaseTransaction',
    'RedisConnection',
    'RedisChannelHandler',
    'redis_channel_handler',
    'StatsdConnection',
    'TimeValue',
    'Paginator',
    'HelpCommand',
    'Formatter',
    'component_check',
    'component_id_check',
    'Embeddify',
    'TwitchStream',
    'minify_html',
    'format',
    'embeddify',
    'DatabaseConnection',
    'Database',
    'Redis',
    'Stats',
    'translation',
    'i18n',
)


_html_minifier = _re.compile(r"\s{2,}|\n")
def minify_html(text: str) -> str:
    return _html_minifier.sub("", text)


format = Formatter().format
embeddify = Embeddify.send
DatabaseConnection = DatabaseWrapper
Database = DatabaseWrapper
Redis = RedisConnection
Stats = StatsdConnection
