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

from . import gateway
from ._util import *
from .application import *
from .audit_log import *
from .auto_moderation import *
from .channel import *
from .components import *
from .embed import *
from .emoji import *
from .guild import *
from .guild_scheduled_event import *
from .guild_template import *
from .interaction import *
from .invite import *
from .locale import *
from .message import *
from .stage_instance import *
from .sticker import *
from .user import *
from .voice import *
from .webhook import *

__all__: tuple[str, ...] = (
    'ActionRow',
    'Activity',
    'AllowedMentions',
    'Application',
    'ApplicationRoleConnection',
    'ApplicationRoleConnectionMetadata',
    'ApplicationTeam',
    'ApplicationTeamMember',
    'Attachment',
    'AuditEntryInfo',
    'AuditLog',
    'AuditLogChange',
    'AuditLogEntry',
    'AuditLogEvent',
    'AutoModerationAction',
    'AutoModerationActionMetadata',
    'AutoModerationActionType',
    'AutoModerationKeywordPresetType',
    'AutoModerationRule',
    'AutoModerationTriggerMetadata',
    'AutoModerationTriggerType',
    'AutoModeratorEventType',
    'Ban',
    'Button',
    'Channel',
    'ChannelMention',
    'ChannelOverwrite',
    'ChannelType',
    'ComponentType',
    'Embed',
    'EmbedType',
    'Emoji',
    'GatewayGuild',
    'Guild',
    'GuildFeature',
    'GuildMember',
    'GuildPreview',
    'GuildScheduledEvent',
    'GuildScheduledEventEntityMetadata',
    'GuildScheduledEventUser',
    'GuildTemplate',
    'GuildWelcomeScreen',
    'GuildWelcomeScreenChannel',
    'GuildWidget',
    'HasLocalizations',
    'InstallParams',
    'Integration',
    'IntegrationAccount',
    'IntegrationApplication',
    'InteractionType',
    'Invite',
    'InviteWithMetadata',
    'Locale',
    'Message',
    'MessageActivity',
    'MessageComponent',
    'MessageInteraction',
    'MessageReference',
    'PartialEmoji',
    'PartialSticker',
    'PartialUser',
    'Presence',
    'Reaction',
    'Role',
    'RoleTags',
    'SelectMenu',
    'SelectOption',
    'Snowflake',
    'StageInstance',
    'Sticker',
    'StickerPack',
    'TextInput',
    'ThreadMember',
    'ThreadMetadata',
    'Timestamp',
    'UnavailableGuild',
    'User',
    'UserConnection',
    'VoiceRegion',
    'VoiceState',
    'Webhook',
    'gateway',
)


"""
The payloads subpackage contains the payload classes for each payload type
from Discord. These will mostly be used to type hint payloads, and won't be
super helpful externally in the library.

These classes will generally not have docstrings unless necessary to understand
them.

Of note here: snowflakes (IDs) will be documented as strings as thats's what
the Discord API returns. This is regardless of the fact that the library treats
them as integers within classes.
"""
