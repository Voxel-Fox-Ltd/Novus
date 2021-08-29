novus
==========

.. image:: https://discord.com/api/guilds/208895639164026880/embed.png
   :target: https://discord.gg/vfl
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/novus.svg
   :target: https://pypi.python.org/pypi/novus
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/novus.svg
   :target: https://pypi.python.org/pypi/novus
   :alt: PyPI supported Python versions

A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U novus

    # Windows
    py -3 -m pip install -U novus

Otherwise to get voice support you should run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "novus[voice]"

    # Windows
    py -3 -m pip install -U novus[voice]


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/Voxel-Fox-Ltd/novus
    $ cd novus
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)

Please note that on Linux installing voice you must install the following packages via your favourite package manager (e.g. ``apt``, ``dnf``, etc) before running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.6-dev`` for Python 3.6)

Quick Example
--------------

.. code:: py

    import discord

    class MyClient(discord.Client):
        async def on_ready(self):
            print('Logged on as', self.user)

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

    client = MyClient()
    client.run('token')

Bot Example
~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

You can find more examples in the examples directory.

Links
------

- `Documentation <https://novus.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/vfl>`_
- `Discord API <https://discord.gg/discord-api>`_
