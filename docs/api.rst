API Reference
==============

ABCs and Mixins
---------------------

.. autoclass:: novus.abc.Snowflake

.. autoclass:: novus.abc.StateSnowflake

.. autoclass:: novus.mixins.Messageable
    :members:

Enums
------

.. class:: novus.Locale

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

.. class:: novus.ChannelType

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

.. class:: novus.PermissionOverwriteType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``role``
        * - ``member``

Guild
~~~~~~

.. class:: novus.NSFWLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``default``
        * - ``explicit``
        * - ``safe``
        * - ``age_restricted``

.. class:: novus.PremiumTier

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``tier_1``
        * - ``tier_2``
        * - ``tier_3``

.. class:: novus.MFALevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``elevated``

.. class:: novus.ContentFilterLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``disabled``
        * - ``members_without_roles``
        * - ``all_members``

.. class:: novus.VerificationLevel

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

.. class:: novus.NotificationLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``all_messages``
        * - ``only_mentions``

Sticker
~~~~~~~

.. class:: novus.StickerType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``standard``
        * - ``guild``

.. class:: novus.StickerFormat

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``png``
        * - ``apng``
        * - ``lottie``
        * - ``gif``

User
~~~~~~~

.. class:: novus.UserPremiumType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``nitro_classic``
        * - ``nitro``
        * - ``nitro_basic``

Auto Moderation
~~~~~~~~~~~~~~~

.. class:: novus.AutoModerationKeywordPresetType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``profanity``
        * - ``sexual_content``
        * - ``slurs``

.. class:: novus.AutoModerationTriggerType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``keyword``
        * - ``spam``
        * - ``keyword_preset``
        * - ``mention_spam``

.. class:: novus.AutoModerationEventType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``message_send``

.. class:: novus.AutoModerationActionType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``block_message``
        * - ``send_alert_message``
        * - ``timeout``

Scheduled Event
~~~~~~~~~~~~~~~

.. class:: novus.EventPrivacyLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``guild_only``

.. class:: novus.EventStatus

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``scheduled``
        * - ``active``
        * - ``completed``
        * - ``cancelled``

.. class:: novus.EventEntityType

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``stage_instance``
        * - ``voice``
        * - ``external``

Flags
------

Application
~~~~~~~~~~~~

.. class:: novus.ApplicationFlags

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

.. class:: novus.MessageFlags

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``suppress_join_notifications``
        * - ``suppress_premium_subscriptions``
        * - ``suppress_guild_reminder_notifications``
        * - ``suppress_join_notification_replies``

Guild
~~~~~~

.. class:: novus.SystemChannelFlags

    Flags for a system channel within a guild.

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``suppress_join_notifications``
        * - ``suppress_premium_subscriptions``
        * - ``suppress_guild_reminder_notifications``
        * - ``suppress_join_notification_replies``

.. class:: novus.Permissions

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

.. class:: novus.UserFlags

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

.. class:: novus.AuditLogEntryType

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

.. autoclass:: novus.User
    :members:
    :inherited-members:
    :no-members: __init__

GuildMember
~~~~~~~~~~~

.. autoclass:: novus.GuildMember
    :members:
    :inherited-members:
    :no-members: __init__

Guild
~~~~~

.. autoclass:: novus.Guild
    :members:
    :inherited-members:
    :no-members: __init__

.. autoclass:: novus.PartialGuild
    :members:
    :inherited-members:
    :no-members: __init__

Invite
~~~~~~

.. autoclass:: novus.Invite
    :members:
    :inherited-members:
    :no-members: __init__

StageInstance
~~~~~~~~~~~~~

.. autoclass:: StageInstance
    :members:
    :inherited-members:
    :no-members: __init__

Audit Logs
~~~~~~~~~~

.. autoclass:: novus.AuditLog
    :members:
    :no-members: __init__

.. autoclass:: novus.AuditLogEntry
    :members:
    :no-members: __init__

.. autoclass:: novus.AuditLogContainer
    :members:
    :no-members: __init__

Sticker
~~~~~~~

.. autoclass:: novus.Sticker
    :members:
    :inherited-members:
    :no-members: __init__

Emoji
~~~~~

.. autoclass:: novus.Emoji
    :members:
    :inherited-members:
    :no-members: __init__

Role
~~~~

.. autoclass:: novus.Role
    :members:
    :inherited-members:
    :no-members: __init__

Message
~~~~~~~

.. autoclass:: novus.Message
    :members:
    :inherited-members:
    :no-members: __init__

Auto Moderation
~~~~~~~~~~~~~~~

.. autoclass:: novus.AutoModerationRule
    :members:
    :inherited-members:
    :no-members: __init__

Auto Moderation
~~~~~~~~~~~~~~~

.. autoclass:: novus.ScheduledEvent
    :members:
    :inherited-members:
    :no-members: __init__

Discord Oauth Models
------------------------

Oauth models are much the same as other models, but returned when you're
authenticated via an Oauth access token.

.. autoclass:: novus.OauthGuild
    :members:
    :inherited-members:
    :no-members: __init__

Discord Data Containers
-----------------------

These are models are designed for you to initialize yourself so as to use them in API methods. They may also be returned from API methods.

.. autoclass:: novus.Object
    :special-members: __init__
    :members:

.. autoclass:: novus.AllowedMentions
    :special-members: __init__
    :members:

.. autoclass:: novus.Embed
    :special-members: __init__
    :members:

.. autoclass:: novus.File
    :special-members: __init__
    :members:

.. autoclass:: novus.MessageReference
    :special-members: __init__
    :members:

.. autoclass:: novus.PermissionOverwrite
    :special-members: __init__
    :members:

.. autoclass:: novus.AutoModerationAction
    :special-members: __init__
    :members:

.. autoclass:: novus.AutoModerationTriggerMetadata
    :special-members: __init__
    :members:


Proxy Objects
-------------

These are models returned from the API that you aren't intended to make yourself.

.. autoclass:: novus.WelcomeScreen
    :members:
    :no-members: __init__

.. autoclass:: novus.GuildPreview
    :members:
    :no-members: __init__

.. autoclass:: novus.GuildBan
    :members:
    :no-members: __init__

.. autoclass:: novus.Asset
    :members: get_url
    :no-members: __init__

API
----

.. autoclass:: novus.api._route.Route

.. autoclass:: novus.api.HTTPConnection
    :no-members:

.. autoclass:: novus.api.application_role_connection_metadata.ApplicationRoleHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.audit_log.AuditLogHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.auto_moderation.AutoModerationHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.channel.ChannelHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.emoji.EmojiHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.guild.GuildHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.guild_scheduled_event.GuildEventHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.guild_template.GuildTemplateHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.invite.InviteHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.stage_instance.StageHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.sticker.StickerHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.user.UserHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.voice.VoiceHTTPConnection
    :members:
    :no-members: __init__

.. autoclass:: novus.api.webhook.WebhookHTTPConnection
    :members:
    :no-members: __init__
