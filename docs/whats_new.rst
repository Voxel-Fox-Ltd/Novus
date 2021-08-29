.. currentmodule:: discord

.. |commands| replace:: [:ref:`ext.commands <discord_ext_commands>`]
.. |tasks| replace:: [:ref:`ext.tasks <discord_ext_tasks>`]

.. _whats_new:

Changelog
============

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. _vp0_0_1:

v0.0.1
--------

The new and changed features described in this section refer to changes from Rapptz's original Discord.py repo.

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

* Message components are now sendable using the :ref:`bot UI kit <_discord_ui_kit>`.
* Slash commands are now processed as message commands if sent through the gateway.
* :func:`Client.register_application_commands` will register all of your bot's loaded commands as application commands.
* Threads as a whole (thanks to Danny).
* Type hinting for a vast majority of the library (thanks to Danny).

.. _vp_rapptz:

Original
--------

Everything at this point and before is forked directly from `Rapptz's Discord.py library <https://github.com/Rapptz/discord.py>`_. The changelogs from before that point (and thus before the existance of this library) have been removed.