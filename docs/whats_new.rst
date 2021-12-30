.. currentmodule:: discord

.. |commands| replace:: [:ref:`ext.commands <discord_ext_commands>`]
.. |tasks| replace:: [:ref:`ext.tasks <discord_ext_tasks>`]

.. _whats_new:

Changelog
============

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. _vp0_0_6:

v0.0.6
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add ``guild_locale``, ``user_locale``, and ``locale`` to :class:`Interaction` and the two context objects.
* Add :attr:`ApplicationCommand.default_permission`.

Changed Features
~~~~~~~~~~~~~~~~~~~

* Change all args in :class:`ApplicationCommandOptionChoice`, :class:`ApplicationCommandOption`, and :class:`ApplicationCommand`'s inits to be kwargs instead of positional args.

.. _vp0_0_5:

v0.0.5
--------

New Features
~~~~~~~~~~~~~~~~~~

* Added support for :class:`modals <ui.Modal>`.
* Add :attr:`Interaction.components`.
* Add :class:`ApplicationCommandInteractionDataOption`.
* Add :class:`ui.InteractionComponent`.
* Add support for role icons.
* Add support for member timeouts.
    * Add :func:`Member.disable_communication_until`.
    * Add :func:`Member.disable_communication_for`.
    * Add :func:`Member.enable_communication`.

Changed Features
~~~~~~~~~~~~~~~~~~~

* :ref:`Autocomplete is now documented <on_autocomplete_interaction>`.
* Changed the types of :attr:`Interaction.values` and :attr:`Interaction.options`.

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fixed typing of :func:`Member.move_to`.
* Add proper exports for ``discord.ui``.

.. _vp0_0_4:

v0.0.4
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add :attr:`ApplicationCommandOption.channel_types`.
* Add ``files`` parameter to :func:`InteractionResponse.send`.
* Add support for autocomplete.
    * Add :attr:`ApplicationCommandOption.autocomplete`.
    * Add :attr:`Interaction.options`.
    * Add :func:`on_autocomplete_interaction` and :func:`commands.Bot.on_autocomplete` events.
* Add ``ignore_spaces`` kwarg to ``Bot.get_command``.
* Add :func:`MessageComponents.add_number_buttons`.
* Add :func:`Button.confirm` and :func:`Button.cancel`.
* Add ``options`` kwarg to `ApplicationCommand`.
* Add :attr:`Interaction.command_name`.
* Add :attr:`ApplicationCommandOption.channel_types`.
* Add ``@is_slash_command`` check.

Changed Features
~~~~~~~~~~~~~~~~~~~

* Change default response type to nothing.

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fix adding slash commands which we say not to add.
* Fix component deferring.
* Fix popping non-existent keys.
* Re-add options to ApplicationCommandOption export.
* Fix reccursion error in interactionresolved.

.. _vp0_0_3:

v0.0.3
--------

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fix indentation on getting application command arg type.
* Fix application command ``required`` property not being set properly.
* Add import for application commands to ``discord`` top-level package.
* Filter context menu commands out of the default help menu implementation.

Changed Features
~~~~~~~~~~~~~~~~~~

* Removed Danny's ``on_socket_event_type`` to be replaced with :func:`on_socket_event`.
* The ``newcog`` cmd argument will now use VoxelBotUtils if it's installed.
* A list of :class:`commands.Command` objects are now allowed to be passed into :func:`ext.commands.Bot.register_application_commands`.

New Features
~~~~~~~~~~~~~~~~~~

* Add :class:`InteractionResolved` class, as a new attribute in :class:`Interaction`.
* Added :func:`commands.context_command` decorator.
* Added :func:`utils.naive_dt`.
* Add :func:`Embed.remove_image` and :func:`Embed.remove_thumbnail`.
* Add :class:`WelcomeScreen`.
* Add :func:`ext.commands.get_interaction_route_table`.

.. _vp0_0_2:

v0.0.2
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add :func:`defer decorator<commands.defer>` for application commands.
* Add :func:`InteractionResonse.defer_update`.
* Add ``allowed_mentions`` to :func:`InteractionReponse.edit_message`.
* Add ``response_type`` kwarg to :func:`utils.oauth_url`.

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fix action rows not being parsed correctly.
* Fixed ``ephemeral`` kwarg in :func:`commands.SlashContext.send` and :func:`commands.SlashContext.defer`.
* Fix slash commands not working with cooldowns.


.. _vp0_0_1:

v0.0.1
--------

The new and changed features described in this section refer to changes from Rapptz's original Discord.py repo. You can see :ref:`a whole list of changes <migrating_2_0>` here, but this section will go over the main ones.

Breaking Changes
~~~~~~~~~~~~~~~~~~

* ``TextChannel.get_partial_message`` is now pos-only
* ``permissions_for`` is now pos-only
* ``GroupChannel.owner`` is now Optional
* ``edit`` methods now only accept None if it actually means something (e.g. clearing it)
* Separate ``on_member_update`` and ``on_presence_update``
    * The new event ``on_presence_update`` is now called when status/activity is changed.
    * ``on_member_update`` will now no longer have status/activity changes.
* ``afk`` parameter in ``Client.change_presence`` is removed
* The undocumented private ``on_socket_response`` event got removed.
    * Consider using the newer documented ``on_socket_event_type`` event instead.
* Using ``on_socket_raw_receive`` and ``on_socket_raw_send`` are now opt-in via enable_debug_events toggle.
* ``on_socket_raw_receive`` is now only dispatched after decompressing the payload.
* All ``get_`` lookup functions now use positional-only parameters for the id parameter.
* ``User.avatar`` now returns ``None`` if the user did not upload an avatar.
    * Use ``User.display_avatar`` to get the avatar and fallback to the default avatar to go back to the old behaviour.

New Features
~~~~~~~~~~~~~~~~

* Message components are now sendable using the :ref:`bot UI kit <discord_ui_kit>`.
* Slash commands are now processed as message commands if sent through the gateway.
* :func:`Client.register_application_commands` will register all of your bot's loaded commands as application commands.
* Threads as a whole (thanks to Danny).
* Type hinting for a vast majority of the library (thanks to Danny).

.. _vp_rapptz:

Original
--------

Everything at this point and before is forked directly from `Rapptz's Discord.py library <https://github.com/Rapptz/discord.py>`_. The changelogs from before that point (and thus before the existance of this library) have been removed.


