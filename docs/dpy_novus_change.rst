.. _dpy_novus_change:

Discord.py and Novus Changes
================================================

Novus is a fork from Dpy 2.0, where most people would have been running on Dpy 1.7. Because this is a major version change, there's a few breaking changes between versions. Here is a whole list of removed features in Novus, as well as a [complete up to Novus 0.0.2] list of new features.

Removed in Novus
-------------------------------

Main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``discord.Client.request_offline_members``
* ``discord.Client.logout`` (use :func:`discord.Client.close`)
* ``discord.Client.fetch_user_profile``
* ``discord.AutoShardedClient.request_offline_members``
* ``discord.AppInfo.icon_url`` (use :attr:`discord.AppInfo.icon` and :attr:`discord.Asset.url`)
* ``discord.AppInfo.icon_url_as`` (use :attr:`discord.AppInfo.icon`)
* ``discord.AppInfo.cover_image_url`` (use :attr:`discord.AppInfo.cover_image` and :attr:`discord.Asset.url`)
* ``discord.AppInfo.cover_image_url_as`` (use :attr:`discord.AppInfo.cover_image`)
* ``discord.Team.icon_url`` (use :attr:`discord.Team.icon` and :attr:`discord.Asset.url`)
* ``discord.Team.icon_url_as`` (use :attr:`discord.Team.icon`)
* ``discord.VoiceClient.on_voice_state_update`` (use :func:`discord.VoiceProtocol.on_voice_state_update`)
* ``discord.VoiceClient.on_voice_server_update`` (use :func:`discord.VoiceProtocol.on_voice_server_update`)
* ``discord.VoiceClient.connect`` (use :func:`discord.VoiceProtocol.connect`)
* ``discord.on_private_channel_delete`` (removed with selfbot code)
* ``discord.on_relationship_add`` (removed with selfbot code)
* ``discord.on_relationship_update`` (removed with selfbot code)
* ``discord.Profile`` (removed with selfbot code)
* ``discord.HypeSquadHouse`` (removed with selfbot code)
* ``discord.VerificationLevel.table_flip`` (aliases removed)
* ``discord.VerificationLevel.extreme`` (aliases removed)
* ``discord.VerificationLevel.double_table_flip`` (aliases removed)
* ``discord.VerificationLevel.very_high`` (aliases removed)
* ``discord.RelationshipType`` (removed with selfbot code)
* ``discord.UserContentFilter`` (removed with selfbot code)
* ``discord.FriendFlags`` (removed with selfbot code)
* ``discord.PremiumType`` (removed with selfbot code)
* ``discord.Theme`` (removed with selfbot code)
* ``discord.StickerType.png`` (use :attr:`discord.StickerFormatType.png`)
* ``discord.StickerType.apng`` (use :attr:`discord.StickerFormatType.apng`)
* ``discord.StickerType.lottie`` (use :attr:`discord.StickerFormatType.lottie`)
* ``discord.Webhook.avatar_url`` (use :attr:`discord.Webhook.avatar` and :attr:`discord.Asset.url`)
* ``discord.Webhook.avatar_url_as`` (use :attr:`discord.Webhook.avatar`)
* ``discord.Webhook.execute`` (no direct alternative - see :class:`discord.Webhook`)
* ``discord.WebhookAdapter`` (no direct alternative - see :class:`discord.Webhook`)
* ``discord.AsyncWebhookAdapter`` (no direct alternative - see :class:`discord.Webhook`)
* ``discord.RequestsWebhookAdapter`` (no direct alternative - see :class:`discord.SyncWebhook`)
* ``discord.ClientUser.email`` (removed with selfbot code)
* ``discord.ClientUser.premium`` (removed with selfbot code)
* ``discord.ClientUser.premium_type`` (removed with selfbot code)
* ``discord.ClientUser.get_relationship`` (removed with selfbot code)
* ``discord.ClientUser.relationships`` (removed with selfbot code)
* ``discord.ClientUser.friends`` (removed with selfbot code)
* ``discord.ClientUser.blocked`` (removed with selfbot code)
* ``discord.ClientUser.create_group`` (removed with selfbot code)
* ``discord.ClientUser.edit_settings`` (removed with selfbot code)
* ``discord.ClientUser.avatar_url`` (use :attr:`discord.ClientUser.avatar` and :attr:`discord.Asset.url`)
* ``discord.ClientUser.avatar_url_as`` (use :attr:`discord.ClientUser.avatar`)
* ``discord.ClientUser.default_avatar_url`` (use :attr:`discord.ClientUser.default_avatar` and :attr:`discord.Asset.url`)
* ``discord.ClientUser.is_avatar_animated`` (use :attr:`discord.ClientUser.avatar` and :attr:`discord.Asset.animated`)
* ``discord.ClientUser.permissions_in`` (removed with selfbot code)
* ``discord.Relationship`` (removed with selfbot code)
* ``discord.User.relationship`` (removed with selfbot code)
* ``discord.User.mutual_friends`` (removed with selfbot code)
* ``discord.User.is_friend`` (removed with selfbot code)
* ``discord.User.is_blocked`` (removed with selfbot code)
* ``discord.User.block`` (removed with selfbot code)
* ``discord.User.unblock`` (removed with selfbot code)
* ``discord.User.remove_friend`` (removed with selfbot code)
* ``discord.User.send_friend_request`` (removed with selfbot code)
* ``discord.User.profile`` (removed with selfbot code)
* ``discord.User.avatar_url`` (use :attr:`discord.User.avatar` and :attr:`discord.Asset.url`)
* ``discord.User.avatar_url_as`` (use :attr:`discord.User.avatar` and :attr:`discord.Asset.url`)
* ``discord.User.default_avatar_url`` (use :attr:`discord.User.default_avatar` and :attr:`discord.Asset.url`)
* ``discord.User.is_avatar_animated`` (use :attr:`discord.User.avatar` and :attr:`discord.Asset.animated`)
* ``discord.User.permissions_in`` (use :func:`discord.TextChannel.permissions_for`)
* ``discord.Message.call`` (removed with selfbot code)
* ``discord.Message.ack`` (removed with selfbot code)
* ``discord.Reaction.custom_emoji`` (use :code:`isinstance(reaction.emoji, discord.Emoji)`)
* ``discord.CallMessage`` (removed with selfbot code)
* ``discord.GroupCall`` (removed with selfbot code)
* ``discord.Guild.icon_url`` (use :attr:`discord.Guild.icon` and :attr:`discord.Asset.url`)
* ``discord.Guild.is_icon_animated`` (use :attr:`discord.Guild.icon` and :attr:`discord.Asset.animated`)
* ``discord.Guild.icon_url_as`` (use :attr:`discord.Guild.icon`)
* ``discord.Guild.banner_url`` (use :attr:`discord.Guild.banner` :attr:`discord.Asset.url`)
* ``discord.Guild.banner_url_as`` (use :attr:`discord.Guild.banner`)
* ``discord.Guild.splash_url`` (use :attr:`discord.Guild.splash` :attr:`discord.Asset.url`)
* ``discord.Guild.splash_url_as`` (use :attr:`discord.Guild.splash`)
* ``discord.Guild.discovery_splash_url`` (use :attr:`discord.Guild.discovery_splash` and :attr:`discord.Asset.url`)
* ``discord.Guild.discovery_splash_url_as`` (use :attr:`discord.Guild.discovery_splash`)
* ``discord.Guild.ack`` (removed with selfbot code)
* ``discord.Integration.syncing``
* ``discord.Integration.role``
* ``discord.Integration.enable_emoticons``
* ``discord.Integration.expire_behaviour``
* ``discord.Integration.expire_grace_period``
* ``discord.Integration.synced_at``
* ``discord.Integration.edit``
* ``discord.Integration.sync``
* ``discord.Member.permissions_in`` (use :func:`discord.TextChannel.permissions_for`)
* ``discord.Member.avatar_url`` (use :attr:`discord.Member.avatar` and :attr:`discord.Asset.url`)
* ``discord.Member.avatar_url_as`` (use :attr:`discord.Member.avatar`)
* ``discord.Member.block`` (removed with selfbot code)
* ``discord.Member.default_avatar_url`` (use :attr:`discord.Member.default_avatar` and :attr:`discord.Asset.url`)
* ``discord.Member.is_avatar_animated`` (use :attr:`discord.Member.avatar` and :attr:`discord.Asset.animated`)
* ``discord.Member.is_blocked`` (removed with selfbot code)
* ``discord.Member.is_friend`` (removed with selfbot code)
* ``discord.Member.mutual_friends`` (removed with selfbot code)
* ``discord.Member.profile`` (removed with selfbot code)
* ``discord.Member.relationship`` (removed with selfbot code)
* ``discord.Member.remove_friend`` (removed with selfbot code)
* ``discord.Member.send_friend_request`` (removed with selfbot code)
* ``discord.Member.unblock`` (removed with selfbot code)
* ``discord.Emoji.url_as``
* ``discord.PartialEmoji.url_as``
* ``discord.GroupChannel.icon_url`` (removed with selfbot code)
* ``discord.GroupChannel.icon_url_as`` (removed with selfbot code)
* ``discord.GroupChannel.add_recipients`` (removed with selfbot code)
* ``discord.GroupChannel.remove_recipients`` (removed with selfbot code)
* ``discord.GroupChannel.edit`` (removed with selfbot code)
* ``discord.PartialInviteGuild.icon_url`` (use :attr:`discord.PartialInviteGuild.icon` and :attr:`discord.Asset.url`)
* ``discord.PartialInviteGuild.is_icon_animated`` (use :attr:`discord.PartialInviteGuild.icon` and :attr:`discord.Asset.animated`)
* ``discord.PartialInviteGuild.icon_url_as`` (use :attr:`discord.PartialInviteGuild.icon`)
* ``discord.PartialInviteGuild.banner_url`` (use :attr:`discord.PartialInviteGuild.banner` and :attr:`discord.Asset.url`)
* ``discord.PartialInviteGuild.banner_url_as`` (use :attr:`discord.PartialInviteGuild.banner`)
* ``discord.PartialInviteGuild.splash_url`` (use :attr:`discord.PartialInviteGuild.splash` and :attr:`discord.Asset.url`)
* ``discord.PartialInviteGuild.splash_url_as`` (use :attr:`discord.PartialInviteGuild.splash`)
* ``discord.WidgetMember.avatar_url`` (use :attr:`discord.WidgetMember.avatar` and :attr:`discord.Asset.url`)
* ``discord.WidgetMember.avatar_url_as`` (use :attr:`discord.WidgetMember.avatar`)
* ``discord.WidgetMember.default_avatar_url`` (use :attr:`discord.WidgetMember.default_avatar` and :attr:`discord.Asset.url`)
* ``discord.WidgetMember.is_avatar_animated``(use :attr:`discord.WidgetMember.avatar` and :attr:`discord.Asset.animated`)
* ``discord.WidgetMember.permissions_in`` (use :func:`discord.TextChannel.permissions_for`)
* ``discord.Sticker.image``
* ``discord.Sticker.tags``
* ``discord.Sticker.preview_image``
* ``discord.Sticker.image_url``
* ``discord.Sticker.image_url_as``
* ``discord.MemberCacheFlags.online``

Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``discord.ext.commands.Bot.self_bot``
* ``discord.ext.commands.Bot.fetch_user_profile``
* ``discord.ext.commands.Bot.logout``
* ``discord.ext.commands.Bot.request_offline_members``
* ``discord.ext.commands.HelpCommand.clean_prefix``
* ``discord.ext.commands.MissingPermissions.missing_perms``
* ``discord.ext.commands.BotMissingPermissions.missing_perms``
* ``discord.ext.commands.ExtensionNotFound.original``

Added in Novus
-------------------------------

An incomplete list of new features in Novus up to versin 0.0.2.

Main
~~~~~~~~~~~~~~~~~~~

* :attr:`discord.Client.stickers`
* :attr:`discord.Client.application_id`
* :attr:`discord.Client.application_flags`
* :attr:`discord.Client.status`
* :func:`discord.Client.get_partial_messageable`
* :func:`discord.Client.get_stage_instance`
* :func:`discord.Client.get_sticker`
* :func:`discord.Client.fetch_stage_instance`
* :func:`discord.Client.fetch_sticker`
* :func:`discord.Client.fetch_premium_sticker_packs`
* :func:`discord.Client.create_dm`
* :func:`discord.Client.register_application_commands`
* :attr:`discord.AppInfo.terms_of_service_url`
* :attr:`discord.AppInfo.privacy_policy_url`
* :class:`discord.PartialAppInfo`
* :func:`discord.on_socket_event`
* :func:`discord.on_slash_command`
* :func:`discord.on_component_interaction`
* :func:`discord.on_thread_join`
* :func:`discord.on_thread_remove`
* :func:`discord.on_thread_delete`
* :func:`discord.on_thread_member_join`
* :func:`discord.on_thread_update`
* :func:`discord.on_integration_create`
* :func:`discord.on_integration_update`
* :func:`discord.on_raw_integration_delete`
* :func:`discord.on_presence_update`
* :func:`discord.on_guild_stickers_update`
* :func:`discord.on_stage_instance_create`
* :func:`discord.on_stage_instance_update`
* :func:`discord.utils.utcnow`
* :func:`discord.utils.format_dt`
* :func:`discord.utils.as_chunks`
* :attr:`discord.ChannelType.news_thread`
* :attr:`discord.ChannelType.public_thread`
* :attr:`discord.ChannelType.private_thread`
* :attr:`discord.MessageType.thread_created`
* :attr:`discord.MessageType.reply`
* :attr:`discord.MessageType.application_command`
* :attr:`discord.MessageType.guild_invite_reminder`
* :attr:`discord.MessageType.thread_starter_message`
* :class:`discord.UserFlags`
* :class:`discord.InteractionType`
* :class:`discord.InteractionResponseType`
* :class:`discord.ComponentType`
* :class:`discord.ButtonStyle`
* :attr:`discord.VerificationLevel.highest`
* :attr:`discord.AuditLogAction.stage_instance_create`
* :attr:`discord.AuditLogAction.stage_instance_update`
* :attr:`discord.AuditLogAction.stage_instance_delete`
* :attr:`discord.AuditLogAction.sticker_create`
* :attr:`discord.AuditLogAction.sticker_update`
* :attr:`discord.AuditLogAction.sticker_delete`
* :attr:`discord.AuditLogAction.thread_create`
* :attr:`discord.AuditLogAction.thread_update`
* :attr:`discord.AuditLogAction.thread_delete`
* :attr:`discord.WebhookType.application`
* :attr:`discord.StickerType.standard`
* :attr:`discord.StickerType.guild`
* :class:`discord.StickerFormatType`
* :class:`discord.InviteTarget`
* :class:`discord.VideoQualityMode`
* :class:`discord.StagePrivacyLevel`
* :class:`discord.NSFWLevel`
* :attr:`discord.AuditLogDiff.discovery_splash`
* :attr:`discord.AuditLogDiff.banner`
* :attr:`discord.AuditLogDiff.rules_channel`
* :attr:`discord.AuditLogDiff.public_updates_channel`
* :attr:`discord.AuditLogDiff.privacy_level`
* :attr:`discord.AuditLogDiff.rtc_region`
* :attr:`discord.AuditLogDiff.video_quality_mode`
* :attr:`discord.AuditLogDiff.format_type`
* :attr:`discord.AuditLogDiff.emoji`
* :attr:`discord.AuditLogDiff.description`
* :attr:`discord.AuditLogDiff.available`
* :attr:`discord.AuditLogDiff.archived`
* :attr:`discord.AuditLogDiff.locked`
* :attr:`discord.AuditLogDiff.auto_archive_duration`
* :attr:`discord.AuditLogDiff.default_auto_archive_duration`
* :attr:`discord.Webhook.source_guild`
* :attr:`discord.Webhook.source_channel`
* :attr:`discord.Webhook.fetch`
* :attr:`discord.Webhook.is_authenticated`
* :attr:`discord.Webhook.is_partial`
* :func:`discord.Webhook.fetch_message`
* :class:`discord.SyncWebhook`
* :class:`discord.SyncWebhookMessage`
* :attr:`discord.ClientUser.accent_color`
* :attr:`discord.ClientUser.accent_colour`
* :attr:`discord.ClientUser.banner`
* :attr:`discord.ClientUser.display_avatar`
* :attr:`discord.User.accent_color`
* :attr:`discord.User.accent_colour`
* :attr:`discord.User.banner`
* :attr:`discord.User.display_avatar`
* :attr:`discord.Asset.url`
* :attr:`discord.Asset.key`
* :attr:`discord.Asset.is_animated`
* :func:`discord.Asset.replace`
* :func:`discord.Asset.with_size`
* :func:`discord.Asset.with_format`
* :func:`discord.Asset.with_static_format`
* :attr:`discord.Message.components`
* :func:`discord.Message.create_thread`
* :func:`discord.Reaction.is_custom_emoji`
* :attr:`discord.Guild.stickers`
* :attr:`discord.Guild.nsfw_level`
* :attr:`discord.Guild.threads`
* :func:`discord.Guild.get_channel_or_thread`
* :func:`discord.Guild.get_thread`
* :attr:`discord.Guild.sticker_limit`
* :attr:`discord.Guild.stage_instances`
* :attr:`discord.Guild.get_stage_instance`
* :attr:`discord.Guild.active_threads`
* :func:`discord.Guild.fetch_channel`
* :func:`discord.Guild.fetch_stickers`
* :func:`discord.Guild.fetch_sticker`
* :func:`discord.Guild.create_sticker`
* :func:`discord.Guild.delete_sticker`
* :func:`discord.Guild.delete_emoji`
* :func:`discord.Guild.edit_widget`
* :class:`discord.BotIntegration`
* :class:`discord.IntegrationApplication`
* :class:`discord.StreamIntegration`
* :class:`discord.Interaction`
* :class:`discord.InteractionResolved`
* :class:`discord.InteractionResponse`
* :class:`discord.InteractionMessage`
* :attr:`discord.Member.banner`
* :attr:`discord.Member.accent_color`
* :attr:`discord.Member.accent_colour`
* :attr:`discord.Member.display_avatar`
* :attr:`discord.Member.guild_avatar`
* :func:`discord.Member.get_role`
* :attr:`discord.Spotify.track_url`
* :func:`discord.Emoji.read`
* :func:`discord.Emoji.save`
* :attr:`discord.PartialEmoji.from_str`
* :func:`discord.PartialEmoji.read`
* :func:`discord.PartialEmoji.save`
* :attr:`discord.Role.is_assignable`
* :class:`discord.PartialMessageable`
* :attr:`discord.TextChannel.nsfw`
* :attr:`discord.TextChannel.default_auto_archive_duration`
* :attr:`discord.TextChannel.threads`
* :func:`discord.TextChannel.get_thread`
* :func:`discord.TextChannel.create_thread`
* :attr:`discord.TextChannel.archived_threads`
* :class:`discord.Thread`
* :class:`discord.ThreadMember`
* :attr:`discord.StoreChannel.nsfw`
* :attr:`discord.VoiceChannel.video_quality_mode`
* :attr:`discord.StageChannel.video_quality_mode`
* :attr:`discord.StageChannel.speakers`
* :attr:`discord.StageChannel.listeners`
* :attr:`discord.StageChannel.moderators`
* :attr:`discord.StageChannel.instance`
* :func:`discord.StageChannel.create_instance`
* :func:`discord.StageChannel.fetch_instance`
* :class:`discord.StageInstance`
* :attr:`discord.CategoryChannel.nsfw`
* :attr:`discord.GroupChannel.owner_id`
* :attr:`discord.Invite.expires_at`
* :attr:`discord.Invite.target_type`
* :attr:`discord.Invite.target_user`
* :attr:`discord.Invite.target_application`
* :attr:`discord.Template.is_dirty`
* :attr:`discord.Template.url`
* :attr:`discord.WidgetMember.accent_color`
* :attr:`discord.WidgetMember.accent_colour`
* :attr:`discord.WidgetMember.banner`
* :attr:`discord.WidgetMember.display_avatar`
* :class:`discord.StickerPack`
* :class:`discord.StickerItem`
* :attr:`discord.Sticker.url`
* :class:`discord.StandardSticker`
* :class:`discord.GuildSticker`
* :class:`discord.RawIntegrationDeleteEvent`
* :class:`discord.PartialWebhookGuild`
* :class:`discord.PartialWebhookChannel`
* :func:`discord.Embed.remove_footer`
* :attr:`discord.Intents.emojis_and_stickers`
* :class:`discord.ApplicationFlags`
* :attr:`discord.Colour.brand_green`
* :attr:`discord.Colour.brand_red`
* :attr:`discord.Colour.og_blurple`
* :attr:`discord.Colour.fuchsia`
* :attr:`discord.Colour.yellow`
* :attr:`discord.Activity.buttons`
* :attr:`discord.Permissions.manage_emojis_and_stickers`
* :attr:`discord.Permissions.manage_events`
* :attr:`discord.Permissions.manage_threads`
* :attr:`discord.Permissions.create_public_threads`
* :attr:`discord.Permissions.create_private_threads`
* :attr:`discord.Permissions.external_stickers`
* :attr:`discord.Permissions.use_external_stickers`
* :attr:`discord.Permissions.send_messages_in_threads`
* :attr:`discord.SystemChannelFlags.guild_reminder_notifications`
* :attr:`discord.MessageFlags.has_thread`
* :attr:`discord.MessageFlags.ephemeral`
* :attr:`discord.PublicUserFlags.discord_certified_moderator`
* :class:`discord.ui.BaseComponent`
* :class:`discord.ui.ActionRow`
* :class:`discord.ui.MessageComponents`
* :class:`discord.ui.Button`
* :class:`discord.ui.SelectOption`
* :class:`discord.ui.SelectMenu`
* :class:`discord.InteractionResponded`

Commands
~~~~~~~~~~~~~~~~~~

* :attr:`discord.ext.commands.Bot.application_flags`
* :attr:`discord.ext.commands.Bot.application_id`
* :func:`discord.ext.commands.Bot.close`
* :func:`discord.ext.commands.Bot.create_dm`
* :func:`discord.ext.commands.Bot.fetch_premium_sticker_packs`
* :func:`discord.ext.commands.Bot.fetch_stage_instance`
* :func:`discord.ext.commands.Bot.fetch_sticker`
* :func:`discord.ext.commands.Bot.get_partial_messageable`
* :func:`discord.ext.commands.Bot.get_slash_context`
* :func:`discord.ext.commands.Bot.get_stage_instance`
* :func:`discord.ext.commands.Bot.get_sticker`
* :func:`discord.ext.commands.Bot.process_slash_commands`
* :func:`discord.ext.commands.Bot.register_application_commands`
* :attr:`discord.ext.commands.Bot.status`
* :attr:`discord.ext.commands.Bot.stickers`
* :func:`discord.ext.commands.context_command`
* :attr:`discord.ext.commands.Command.add_slash_command`
* :attr:`discord.ext.commands.Command.param_descriptions`
* :attr:`discord.ext.commands.Command.extras`
* :func:`discord.ext.commands.Command.to_application_command`
* :func:`discord.ext.commands.Group.to_application_command`
* :func:`discord.ext.commands.dynamic_cooldown`
* :func:`discord.ext.commands.defer`
* :class:`discord.ext.commands.Cooldown`
* :attr:`discord.ext.commands.Context.current_parameter`
* :attr:`discord.ext.commands.Context.clean_prefix`
* :class:`discord.ext.commands.ObjectConverter`
* :class:`discord.ext.commands.GuildChannelConverter`
* :class:`discord.ext.commands.ThreadConverter`
* :class:`discord.ext.commands.GuildStickerConverter`
* :func:`discord.ext.commands.run_converters`
* :class:`discord.ext.commands.FlagConverter`
* :class:`discord.ext.commands.Flag`
* :func:`discord.ext.commands.flag`
* :class:`discord.ext.commands.BadLiteralArgument`
* :attr:`discord.ext.commands.CommandOnCooldown.type`
* :class:`discord.ext.commands.ThreadNotFound`
* :class:`discord.ext.commands.GuildStickerNotFound`
* :attr:`discord.ext.commands.MissingPermissions.missing_permissions`
* :attr:`discord.ext.commands.BotMissingPermissions.missing_permissions`
* :class:`discord.ext.commands.FlagError`
* :class:`discord.ext.commands.BadFlagArgument`
* :class:`discord.ext.commands.MissingFlagArgument`
* :class:`discord.ext.commands.TooManyFlags`
* :class:`discord.ext.commands.MissingRequiredFlag`
