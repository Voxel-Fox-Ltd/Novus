API Reference
==============

ABCs and Mixins
---------------------

.. autoclass:: novus.models.abc.Snowflake

.. autoclass:: novus.models.abc.StateSnowflake

.. autoclass:: novus.models.mixins.Messageable
    :members:

Enums
------

.. class:: novus.enums.Locale

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``indonesian``
        * - ``danish``
        * - ``german``
        * - ``uk_english``
        * - ``us_english``
        * - ``spanish``
        * - ``french``
        * - ``croatian``
        * - ``italian``
        * - ``lithuanian``
        * - ``hungarian``
        * - ``dutch``
        * - ``norwegian``
        * - ``polish``
        * - ``brazilian_portuguese``
        * - ``romanian``
        * - ``finnish``
        * - ``swedish``
        * - ``vietnamese``
        * - ``turkish``
        * - ``czech``
        * - ``greek``
        * - ``bulgarian``
        * - ``russian``
        * - ``ukrainian``
        * - ``hindi``
        * - ``thai``
        * - ``china_chinese``
        * - ``japanese``
        * - ``taiwan_chinese``
        * - ``korean``

Channel
~~~~~~~

.. class:: novus.enums.ChannelType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``guild_text``
        * - ``dm``
        * - ``guild_voice``
        * - ``group_dm``
        * - ``guild_category``
        * - ``guild_announcement``
        * - ``announcement_thread``
        * - ``public_thread``
        * - ``private_thread``
        * - ``guild_stage_voice``
        * - ``guild_directory``
        * - ``guild_forum``

.. class:: novus.enums.PermissionOverwriteType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``role``
        * - ``member``

Guild
~~~~~~

.. class:: novus.enums.NSFWLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``default``
        * - ``explicit``
        * - ``safe``
        * - ``age_restricted``

.. class:: novus.enums.PremiumTier

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``tier_1``
        * - ``tier_2``
        * - ``tier_3``

.. class:: novus.enums.MFALevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``elevated``

.. class:: novus.enums.ContentFilterLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``disabled``
        * - ``members_without_roles``
        * - ``all_members``

.. class:: novus.enums.VerificationLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
          - Description
        * - ``none``
          - Unrestricted.
        * - ``low``
          - Must have a verified email on account.
        * - ``medium``
          - Must be registered on Discord for longer than 5 minutes.
        * - ``high``
          - Must be a member of the guild for longer than 10 minutes.
        * - ``very_high``
          - Must have a verified phone number.

.. class:: novus.enums.NotificationLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``all_messages``
        * - ``only_mentions``

Sticker
~~~~~~~

.. class:: novus.enums.StickerType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``standard``
        * - ``guild``

.. class:: novus.enums.StickerFormat

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``png``
        * - ``apng``
        * - ``lottie``
        * - ``gif``

User
~~~~~~~

.. class:: novus.enums.UserPremiumType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``nitro_classic``
        * - ``nitro``
        * - ``nitro_basic``

Auto Moderation
~~~~~~~~~~~~~~~

.. class:: novus.enums.AutoModerationKeywordPresetType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``profanity``
        * - ``sexual_content``
        * - ``slurs``

.. class:: novus.enums.AutoModerationTriggerType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``keyword``
        * - ``spam``
        * - ``keyword_preset``
        * - ``mention_spam``

.. class:: novus.enums.AutoModerationEventType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``message_send``

.. class:: novus.enums.AutoModerationActionType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``block_message``
        * - ``send_alert_message``
        * - ``timeout``


Flags
------

Application
~~~~~~~~~~~~

.. class:: novus.flags.ApplicationFlags

    The public flags for an application.

    .. list-table::
        :header-rows: 1

        * - Attribute
          - Description
        * - ``application_command_badge``
          - Indicates if an app has registered global application commands.
        * - ``embedded``
          - Indicates if an app is embedded within the Discord client
            (currently unavailable publicly).
        * - ``gateway_guild_members``
          - Intent required for bots in 100 or more servers to receive
            member-related events like ``guild_member_add``.
        * - ``gateway_guild_members_limited``
          - Intent required for bots in under 100 servers to receive
            member-related events like ``guild_member_add``.
        * - ``gateway_message_content``
          - Intent required for bots in 100 or more servers to receive message
            content.
        * - ``gateway_message_content_limited``
          - Intent required for bots in under 100 servers to receive message
            content.
        * - ``gateway_presence``
          - Intent required for bots in 100 or more servers to receive
            ``presence_update`` events.
        * - ``gateway_presence_limited``
          - Intent required for bots in under 100 servers to receive
            ``presence_update`` events.
        * - ``verification_pending_guild_limit``
          - Indicates unusual growth of an app that prevents verification.

Message
~~~~~~~

.. class:: novus.flags.MessageFlags

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``suppress_join_notifications``
        * - ``suppress_premium_subscriptions``
        * - ``suppress_guild_reminder_notifications``
        * - ``suppress_join_notification_replies``

Guild
~~~~~~

.. class:: novus.flags.SystemChannelFlags

    Flags for a system channel within a guild.

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``suppress_join_notifications``
        * - ``suppress_premium_subscriptions``
        * - ``suppress_guild_reminder_notifications``
        * - ``suppress_join_notification_replies``

.. class:: novus.flags.Permissions

    A permission set from Discord's API.

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``create_instant_invite``
        * - ``kick_members``
        * - ``ban_members``
        * - ``administrator``
        * - ``manage_channels``
        * - ``manage_guild``
        * - ``add_reactions``
        * - ``view_audit_log``
        * - ``priority_speaker``
        * - ``stream``
        * - ``view_channel``
        * - ``send_messages``
        * - ``send_tts_messages``
        * - ``manage_messages``
        * - ``embed_links``
        * - ``attach_files``
        * - ``read_message_history``
        * - ``mention_everyone``
        * - ``use_external_emojis``
        * - ``view_guild_insights``
        * - ``connect``
        * - ``speak``
        * - ``mute_members``
        * - ``deafen_members``
        * - ``move_members``
        * - ``use_vad``
        * - ``change_nickname``
        * - ``manage_nicknames``
        * - ``manage_roles``
        * - ``manage_webhooks``
        * - ``manage_emojis_and_stickers``
        * - ``use_application_commands``
        * - ``request_to_speak``
        * - ``manage_events``
        * - ``manage_threads``
        * - ``create_public_threads``
        * - ``create_private_threads``
        * - ``use_external_stickers``
        * - ``send_messages_in_threads``
        * - ``use_embedded_activites``
        * - ``moderate_members``

User
~~~~

.. class:: novus.flags.UserFlags

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``staff``
        * - ``partner``
        * - ``hypesquad``
        * - ``bug_hunter_level_1``
        * - ``hypesquad_house_bravery``
        * - ``hypesquad_house_brilliance``
        * - ``hypesquad_house_balance``
        * - ``premium_early_supporter``
        * - ``team_pseudo_user``
        * - ``bug_hunter_level_2``
        * - ``verified_bot``
        * - ``verified_developer``
        * - ``certified_moderator``
        * - ``bot_http_interactions``
        * - ``active_developer``

Audit Log
~~~~~~~~~

.. class:: novus.flags.AuditLogEntryType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``guild_update``
        * - ``channel_create``
        * - ``channel_update``
        * - ``channel_delete``
        * - ``channel_overwrite_create``
        * - ``channel_overwrite_update``
        * - ``channel_overwrite_delete``
        * - ``member_kick``
        * - ``member_prune``
        * - ``member_ban_add``
        * - ``member_ban_remove``
        * - ``member_update``
        * - ``member_role_update``
        * - ``member_move``
        * - ``member_disconnect``
        * - ``bot_add``
        * - ``role_create``
        * - ``role_update``
        * - ``role_delete``
        * - ``invite_create``
        * - ``invite_update``
        * - ``invite_delete``
        * - ``webhook_create``
        * - ``webhook_update``
        * - ``webhook_delete``
        * - ``emoji_create``
        * - ``emoji_update``
        * - ``emoji_delete``
        * - ``message_delete``
        * - ``message_bulk_delete``
        * - ``message_pin``
        * - ``message_unpin``
        * - ``integration_create``
        * - ``integration_update``
        * - ``integration_delete``
        * - ``stage_instance_create``
        * - ``stage_instance_update``
        * - ``stage_instance_delete``
        * - ``sticker_create``
        * - ``sticker_update``
        * - ``sticker_delete``
        * - ``guild_scheduled_event_create``
        * - ``guild_scheduled_event_update``
        * - ``guild_scheduled_event_delete``
        * - ``thread_create``
        * - ``thread_update``
        * - ``thread_delete``
        * - ``application_command_permission_update``
        * - ``auto_moderation_rule_create``
        * - ``auto_moderation_rule_update``
        * - ``auto_moderation_rule_delete``
        * - ``auto_moderation_block_message``
        * - ``auto_moderation_flag_to_channel``
        * - ``auto_moderation_user_communication_disabled``

Utils
-----

.. autofunction:: novus.utils.try_snowflake

.. autofunction:: novus.utils.try_id

.. autofunction:: novus.utils.try_object

Discord Models
--------------

User
~~~~

.. autoclass:: novus.models.User
    :members:
    :inherited-members:
    :no-members: __init__

GuildMember
~~~~~~~~~~~

.. autoclass:: novus.models.GuildMember
    :members:
    :inherited-members:
    :no-members: __init__

Guild
~~~~~

.. autoclass:: novus.models.Guild
    :members:
    :inherited-members:
    :no-members: __init__

.. autoclass:: novus.models.PartialGuild
    :members:
    :inherited-members:
    :no-members: __init__

Invite
~~~~~~

.. autoclass:: novus.models.Invite
    :members:
    :inherited-members:
    :no-members: __init__

Audit Logs
~~~~~~~~~~

.. autoclass:: novus.models.AuditLog
    :members:
    :no-members: __init__

.. autoclass:: novus.models.AuditLogEntry
    :members:
    :no-members: __init__

.. autoclass:: novus.models.AuditLogContainer
    :members:
    :no-members: __init__

Sticker
~~~~~~~

.. autoclass:: novus.models.Sticker
    :members:
    :inherited-members:
    :no-members: __init__

Emoji
~~~~~

.. autoclass:: novus.models.Emoji
    :members:
    :inherited-members:
    :no-members: __init__

Role
~~~~

.. autoclass:: novus.models.Role
    :members:
    :inherited-members:
    :no-members: __init__

Message
~~~~~~~

.. autoclass:: novus.models.Message
    :members:
    :inherited-members:
    :no-members: __init__

Auto Moderation
~~~~~~~~~~~~~~~

.. autoclass:: novus.models.AutoModerationRule
    :members:
    :inherited-members:
    :no-members: __init__

Discord Oauth Models
------------------------

Oauth models are much the same as other models, but returned when you're
authenticated via an Oauth access token.

.. autoclass:: novus.models.OauthGuild
    :members:
    :inherited-members:
    :no-members: __init__

Discord Data Containers
-----------------------

These are models are designed for you to initialize yourself so as to use them in API methods. They may also be returned from API methods.

.. autoclass:: novus.models.Object
    :special-members: __init__
    :members:

.. autoclass:: novus.models.AllowedMentions
    :special-members: __init__
    :members:

.. autoclass:: novus.models.Embed
    :special-members: __init__
    :members:

.. autoclass:: novus.models.File
    :special-members: __init__
    :members:

.. autoclass:: novus.models.MessageReference
    :special-members: __init__
    :members:

.. autoclass:: novus.models.PermissionOverwrite
    :special-members: __init__
    :members:

.. autoclass:: novus.models.AutoModerationAction
    :special-members: __init__
    :members:

.. autoclass:: novus.models.AutoModerationTriggerMetadata
    :special-members: __init__
    :members:


Proxy Objects
-------------

These are models returned from the API that you aren't intended to make yourself.

.. autoclass:: novus.models.WelcomeScreen
    :members:
    :no-members: __init__

.. autoclass:: novus.models.GuildPreview
    :members:
    :no-members: __init__

.. autoclass:: novus.models.GuildBan
    :members:
    :no-members: __init__

.. autoclass:: novus.models.Asset
    :members:
    :no-members: __init__

API
----

.. autoclass:: novus.api.Route

.. autoclass:: novus.api.HTTPConnection
    :no-members:

.. autoclass:: novus.api.ApplicationRoleHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.AuditLogHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.AutoModerationHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.ChannelHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.EmojiHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.GuildHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.GuildEventHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.GuildTemplateHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.InviteHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.StageHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.StickerHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.UserHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.VoiceHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.WebhookHTTPConnection
    :members:
    :no-members: __init__
