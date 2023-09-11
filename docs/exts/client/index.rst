Client
======

The Novus client ext is the easiest way to streamline your bot creation. The
client ext automates aspects of running your bot and handling command
execution, while still allowing you flexibility in how your bot runs and what
it processes.

.. code-block::

   class Pings(client.Plugin):

       @client.command()
       async def pingme(self, ctx: novus.types.CommandI):
           """Ping yourself."""
           await ctx.send(ctx.user.mention)

       @client.command(
           options=[
               novus.ApplicationCommandOption(
                   name="user",
                   type=novus.ApplicationOptionType.user,
                   description="The user you want to ping.",
               )
           ]
       )
       async def ping(self, ctx: novus.types.CommandI, user: novus.User):
           """Ping someone."""
           await ctx.send(user.mention)

.. toctree::
   :maxdepth: 2

   quickstart
   cli
   api
