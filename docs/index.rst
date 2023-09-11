Novus
=================================

Novus is a Python library for interfacing with the
`Discord <https://discord.com>`_ API. It works on a developer-first approach,
and has been designed from the ground up to work with interactions, components,
and slash commands as first-class citizens rather than them being tacked onto
the end of their development 6 years in (thanks Discord).

.. code-block::

   TOKEN: str
   GUILD_ID: int
   USER_ID: int

   # In Novus, a client is a secondary citizen, whereas the HTTP
   # connection is who we love - you can just put down your token
   # and pass that around as necessary
   state = novus.HTTPConnection(TOKEN)

   # As such, models now have classmethods using their state in order
   # to get instances
   guild = await novus.Guild.fetch(state, GUILD_ID)

   # Things that logically inherit (such as Guild -> GuildMember)
   # do also have helper methods
   user1 = await guild.fetch_member(USER_ID)
   user2 = await novus.GuildMember.fetch(state, GUILD_ID, USER_ID)
   assert user1 == user2

The easiest way to get started with Novus in most cases is via the :ref:`Client Quickstart`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/index
   exts/client/index
   configuration
