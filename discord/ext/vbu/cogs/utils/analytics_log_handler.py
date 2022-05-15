import typing
import re
import logging
import json

import aiohttp


class AnalyticsLogHandler(logging.NullHandler):
    """
    This class is explicitly for handling logger data from Discord.py.
    """

    HTTP_EVENT_NAMES = {
        "GET": {
            re.compile(r'/users/([0-9]{15,23})$', re.IGNORECASE): 'get_user',
            re.compile(r'/users/@me/guilds$', re.IGNORECASE): 'get_guilds',
            re.compile(r'/guilds/([0-9]{15,23})$', re.IGNORECASE): 'get_guild',
            re.compile(r'/channels/([0-9]{15,23})$', re.IGNORECASE): 'get_channel',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)$', re.IGNORECASE): 'get_reaction_users',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})$', re.IGNORECASE): 'get_message',
            re.compile(r'/guilds/([0-9]{15,23})/bans$', re.IGNORECASE): 'get_bans',
            re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})$', re.IGNORECASE): 'get_ban',
            re.compile(r'/guilds/([0-9]{15,23})/channels$', re.IGNORECASE): 'get_channels',
            re.compile(r'/guilds/([0-9]{15,23})/members$', re.IGNORECASE): 'get_members',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})$', re.IGNORECASE): 'get_member',
            re.compile(r'/guilds/([0-9]{15,23})/emojis$', re.IGNORECASE): 'get_custom_emojis',
            re.compile(r'/guilds/([0-9]{15,23})/emojis/([0-9]{15,23})$', re.IGNORECASE): 'get_custom_emoji',
            re.compile(r'/guilds/([0-9]{15,23})/audit-logs$', re.IGNORECASE): 'get_audit_logs',
            re.compile(r'/guilds/([0-9]{15,23})/roles$', re.IGNORECASE): 'get_roles',
        },
        "POST": {
            re.compile(r'/channels/([0-9]{15,23})/messages$', re.IGNORECASE): 'send_message',
            re.compile(r'/channels/([0-9]{15,23})/messages/bulk_delete$', re.IGNORECASE): 'bulk_delete',
            re.compile(r'/guilds/([0-9]{15,23})/channels$', re.IGNORECASE): 'create_channel',
            re.compile(r'/guilds/([0-9]{15,23})/emojis$', re.IGNORECASE): 'create_custom_emoji',
            re.compile(r'/interactions/([0-9]{15,23})/([a-zA-Z0-9\-_]+?)/callback$', re.IGNORECASE): 'create_interaction_response',
        },
        "PUT": {
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+?)/@me$', re.IGNORECASE): 'add_reaction',
            re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})$', re.IGNORECASE): 'ban',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})/roles/([0-9]{15,23})$', re.IGNORECASE): 'add_member_role',
            re.compile(r'/channels/([0-9]{15,23})/permissions/([0-9]{15,23})$', re.IGNORECASE): 'edit_channel_permissions',
        },
        "DELETE": {
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})$', re.IGNORECASE): 'delete_message',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})$', re.IGNORECASE): 'kick',
            re.compile(r'/guilds/([0-9]{15,23})/bans/([0-9]{15,23})$', re.IGNORECASE): 'unban',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)/([0-9]{15,23})$', re.IGNORECASE): 'remove_reaction',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)/@me$', re.IGNORECASE): 'remove_reaction',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions$', re.IGNORECASE): 'clear_reactions',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})/reactions/(.+)$', re.IGNORECASE): 'clear_single_reaction',
            re.compile(r'/channels/([0-9]{15,23})$', re.IGNORECASE): 'delete_channel',
            re.compile(r'/guilds/([0-9]{15,23})/emojis/([0-9]{15,23})$', re.IGNORECASE): 'delete_custom_emoji',
            re.compile(r'/guilds/([0-9]{15,23})/roles/([0-9]{15,23})$', re.IGNORECASE): 'delete_role',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})/roles/([0-9]{15,23})$', re.IGNORECASE): 'remove_member_role',
            re.compile(r'/channels/([0-9]{15,23})/permissions/([0-9]{15,23})$', re.IGNORECASE): 'remove_channel_permissions',
        },
        "PATCH": {
            re.compile(r'/guilds/([0-9]{15,23})/members/@me/nick$', re.IGNORECASE): 'change_nickname',
            re.compile(r'/guilds/([0-9]{15,23})/members/([0-9]{15,23})$', re.IGNORECASE): 'edit_member',
            re.compile(r'/channels/([0-9]{15,23})/messages/([0-9]{15,23})$', re.IGNORECASE): 'edit_message',
            re.compile(r'/channels/([0-9]{15,23})$', re.IGNORECASE): 'edit_channel',
            re.compile(r'/guilds/([0-9]{15,23})$', re.IGNORECASE): 'edit_guild',
            re.compile(r'/guilds/([0-9]{15,23})/roles/([0-9]{15,23})$', re.IGNORECASE): 'edit_role',
            re.compile(r'/guilds/([0-9]{15,23})/roles$', re.IGNORECASE): 'move_role_position',
        },
    }
    WEBHOOK_EVENT_NAMES = {
        "POST": {
            re.compile(r'/webhooks/([0-9]{16,23})/([a-zA-Z0-9\-_]+?)$', re.IGNORECASE): 'send_webhook_message',
            re.compile(r'/webhooks/([0-9]{16,23})/([a-zA-Z0-9\-_]+?)/messages/([0-9]{16,23})$', re.IGNORECASE): 'edit_webhook_message',
        },
        "DELETE": {
            re.compile(r'/webhooks/([0-9]{16,23})/([a-zA-Z0-9\-_]+?)/messages/([0-9]{16,23})$', re.IGNORECASE): 'delete_message',
        },
    }
    MESSAGE_DECONSTRUCTOR = re.compile(r"^(?P<method>.+) https://discord(:?app)?.(?:com|gg)/api/v\d(?P<endpoint>.+) with (?P<payload>.+) has returned (?P<status>\d+)$")
    WEBHOOK_MESSAGE_DECONSTRUCTOR = re.compile(r"^Webhook ID (?P<webhookid>.+) with (?P<method>.+) https://discord(:?app)?.(?:com|gg)/api/v\d(?P<endpoint>.+) has returned status code (?P<status>\d+)$")

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @classmethod
    def get_http_event_name(cls, increment: str, method: str, url: str) -> typing.Optional[str]:
        """
        Get the name of the event that we want to increment.
        """

        if increment.startswith("discord.http"):
            possible_endpoints = cls.HTTP_EVENT_NAMES.get(method.upper(), {})
        elif increment.startswith("discord.webhook"):
            possible_endpoints = cls.WEBHOOK_EVENT_NAMES.get(method.upper(), {})
        else:
            return None
        for endpoint_regex, event_name in possible_endpoints.items():
            if endpoint_regex.search(str(url)):
                return event_name
        return None

    def handle(self, record: logging.LogRecord):
        """
        Override handle so we can also statsd incremement.
        """

        message = record.getMessage()
        self.bot.loop.create_task(self.log_response(message))
        return super().handle(record)

    async def log_response(self, message):
        """
        Log our response.
        """

        match = self.MESSAGE_DECONSTRUCTOR.search(message)
        if match is not None:
            return await self.log_message_increment("discord.http", match)
        match = self.WEBHOOK_MESSAGE_DECONSTRUCTOR.search(message)
        if match is not None:
            return await self.log_message_increment("discord.webhook", match)

    async def log_message_increment(self, increment, match):
        """
        Send that actual statsd increment.
        """

        event_name = self.get_http_event_name(increment, match.group("method"), match.group("endpoint"))
        if event_name is None:
            return
        async with self.bot.stats() as stats:
            stats.increment(increment, tags={
                "endpoint": event_name,
                "status_code": int(match.group("status")),
                "status_code_class": match.group("status")[0] + "x" * (len(match.group("status")) - 1)
            })


class AnalyticsClientSession(aiohttp.ClientSession):

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def log_message_increment(self, response):
        url = f"{response.url.host}{response.url.path}"
        status = response.status
        async with self.bot.stats() as stats:
            stats.increment("discord.bot.http", tags={
                "url": url,
                "method": response.method,
                "query": json.dumps(dict(response.url.query), sort_keys=True),
                "status_code": status,
                "status_code_class": str(status)[0] + "x" * (len(str(status)) - 1)
            })

    async def _request(self, *args, **kwargs):
        v = await super()._request(*args, **kwargs)
        self.bot.loop.create_task(self.log_message_increment(v))
        return v
