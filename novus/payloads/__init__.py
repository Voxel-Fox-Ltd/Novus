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

__all__ = (
    # _util
    'Snowflake',
    'Timestamp',
    'HasLocalizations',

    # application
    'ApplicationTeamMember',
    'ApplicationTeam',
    'InstallParams',
    'Application',

    # audit_log
    'AuditLogEvent',
    'AuditEntryInfo',
    'AuditLogChange',
    'AuditLogEntry',
    'AuditLog',

    # auto_moderation
    'AutoModerationTriggerType',
    'AutoModerationKeywordPresetType',
    'AutoModeratorEventType',
    'AutoModerationActionType',
    'AutoModerationActionMetadata',
    'AutoModerationTriggerMetadata',
    'AutoModerationAction',
    'AutoModerationRule',

    # channel
    'Channel',
    'ChannelType',
    'ChannelOverwrite',
    'ThreadMetadata',
    'ThreadMember',

    # components
    'ComponentType',
    'Button',
    'SelectOption',
    'SelectMenu',
    'TextInput',
    'ActionRow',
    'MessageComponent',

    # embed
    'Embed',
    'EmbedType',

    # emoji
    'Emoji',
    'PartialEmoji',

    # guild
    'RoleTags',
    'Role',
    'GuildWidget',
    'GuildPreview',
    'UnavailableGuild',
    'GuildWelcomeScreenChannel',
    'GuildWelcomeScreen',
    'GuildFeature',
    'Guild',
    'GatewayGuild',
    'IntegrationApplication',
    'IntegrationAccount',
    'Integration',
    'Ban',

    # guild_scheduled_event
    'GuildScheduledEvent',
    'GuildScheduledEventEntityMetadata',
    'GuildScheduledEventUser',

    # guild_template
    'GuildTemplate',

    # interaction
    'InteractionType',
    'MessageInteraction',

    # invite
    'Invite',
    'InviteWithMetadata',

    # locale
    'Locale',

    # message
    'Attachment',
    'AllowedMentions',
    'ChannelMention',
    'Reaction',
    'MessageActivity',
    'MessageReference',
    'Message',

    # stage_instance
    'StageInstance',

    # sticker
    'Sticker',
    'PartialSticker',
    'StickerPack',

    # user
    'PartialUser',
    'User',
    'GuildMember',
    'UserConnection',
    'ApplicationRoleConnectionMetadata',
    'ApplicationRoleConnection',
    'Activity',
    'Presence',

    # voice
    'VoiceState',
    'VoiceRegion',

    # webhook
    'Webhook',
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
