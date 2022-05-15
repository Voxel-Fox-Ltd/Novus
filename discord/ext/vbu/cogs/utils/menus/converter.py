from __future__ import annotations

import asyncio
import typing

import discord
from discord.ext import commands

from .check import Check, ModalCheck
from .errors import ConverterFailure, ConverterTimeout
from .utils import get_discord_converter

if typing.TYPE_CHECKING:
    AnyConverter = typing.Union[
        typing.Callable[[typing.Union[str, discord.Interaction[str]]], typing.Any],
        typing.Type[discord.Role],
        typing.Type[discord.TextChannel],
        typing.Type[discord.User],
        typing.Type[discord.Member],
        typing.Type[discord.VoiceChannel],
        typing.Type[str],
        typing.Type[int],
        typing.Type[bool],
    ]


class _FakeConverter(object):

    def __init__(self, callback):
        self.callback = callback

    async def convert(self, ctx, value):
        return self.callback(value)


class Converter(object):
    """
    An object for use in the settings menus for describing things that the user should input.
    """

    def __init__(
            self,
            prompt: str,
            checks: typing.List[Check] = None,
            converter: AnyConverter = str,
            components: discord.ui.MessageComponents = None,
            timeout_message: str = None):
        """
        Args:
            prompt (str): The message that should be sent to the user when asking for the convertable.
            checks (typing.List[voxelbotutils.menus.Check]): A list of check objects that should be used to make sure the user's
                input is valid. These will be silently ignored if a :code:`components` parameter is passed.
            converter (typing.Union[typing.Callable[[str], typing.Any], commands.Converter]): A callable that
                will be used to convert the user's input. If a converter fails then :code:`None` will be returned,
                so use the given checks to make sure that this does not happen if this behaviour is undesirable. If you set
                :code:`components`, then this function should instead take the payload instance that was given back by the
                user's interaction.
            components (voxelbotutils.MessageComponents): An instance of message components to be sent by the bot.
                If components are sent then the bot will not accept a message as a response, only an interaction
                with the component.
            timeout_message (str): The message that should get output to the user if this converter times out.
        """

        self.prompt = prompt
        self.checks = checks or list()
        self._converter = converter
        self.converter = self._wrap_converter(converter)
        self.components = components
        self.timeout_message = timeout_message

    @staticmethod
    def _wrap_converter(converter):
        """
        Wrap the converter so that it always has a `.convert` method.
        """

        converter = get_discord_converter(converter)
        if hasattr(converter, "convert"):
            try:
                return converter()
            except TypeError:
                return converter
        return _FakeConverter(converter)

    async def run(self, ctx: commands.SlashContext, messages_to_delete: list = None):
        """
        Ask the user for an input, run the checks, run the converter, and return. Timeout errors
        *will* be raised here, but they'll propogate all the way back up to the main menu instance,
        which allows the bot to handle those much more gracefully instead of on a converter-by-converter
        basis.
        """

        # Ask the user for an input
        messages_to_delete = messages_to_delete if messages_to_delete is not None else list()

        # The input will be an interaction - branch off here
        if self.components:

            # Send message to respond to
            sent_message = await ctx.interaction.followup.send(self.prompt, components=self.components)
            messages_to_delete.append(sent_message)

            # Set up checks
            def get_button_check(given_message):
                def button_check(payload):
                    if payload.message.id != given_message.id:
                        return False
                    if payload.user.id == ctx.interaction.user.id:
                        return True
                    ctx.bot.loop.create_task(payload.respond(
                        f"Only {ctx.interaction.user.mention} can interact with these buttons.",
                        ephemeral=True,
                    ))
                    return False
                return button_check

            # Wait for the user to click a button
            try:
                payload = await ctx.bot.wait_for(
                    "component_interaction",
                    check=get_button_check(sent_message),
                    timeout=60.0,
                )
                ctx.interaction = payload
                await payload.response.defer_update()
            except asyncio.TimeoutError:
                raise ConverterTimeout(self.timeout_message)

            # And convert
            return await self.converter.convert(ctx, payload)

        # Loop until a valid input is received
        to_send_failure_message = None
        while True:

            # Send a clickable button for the data
            button = discord.ui.Button(label="Set data")
            components = discord.ui.MessageComponents.add_buttons_with_rows(button)
            sent_message = await ctx.interaction.followup.send(
                to_send_failure_message or self.prompt,
                components=components,
                allowed_mentions=discord.AllowedMentions.none(),
                wait=True,
            )

            # Wait for the button to be clicked
            button_click: discord.Interaction = await ctx.bot.wait_for(
                "component_interaction",
                check=lambda i: i.user.id == ctx.interaction.user.id and i.custom_id == button.custom_id,
                timeout=60.0,
            )
            ctx.interaction = button_click  # Don't defer this one so we can send a modal

            # Wait for an input
            modal = discord.ui.Modal(
                title="Menu Data",
                components=[
                    discord.ui.ActionRow(
                        discord.ui.InputText(
                            label="Set data",
                        ),
                    ),
                ],
            )
            await button_click.response.send_modal(modal)
            modal_submission: discord.Interaction = await ctx.bot.wait_for(
                "modal_submit",
                check=lambda i: i.user.id == ctx.interaction.user.id and i.custom_id == modal.custom_id,
                timeout=60.0,
            )
            ctx.interaction = modal_submission
            await modal_submission.response.defer_update()

            # Delete the original message, just for fun
            try:
                await sent_message.delete()
            except:
                pass

            # sent_message = await ctx.send(self.prompt, components=self.components)
            # messages_to_delete.append(sent_message)

            # # Wait for an input
            # user_message = await ctx.bot.wait_for("message", check=check, timeout=60.0)
            # messages_to_delete.append(user_message)

            # # Run it through our checks
            # checks_failed = False
            # for c in self.checks:
            #     try:
            #         checks_failed = not c.check(user_message)
            #     except Exception:
            #         checks_failed = True
            #     if checks_failed:
            #         break

            # Run it through our checks
            checks_failed = False
            c = None
            for c in self.checks:
                try:
                    assert isinstance(c, ModalCheck)
                    checks_failed = not c.check(modal_submission)
                except Exception:
                    checks_failed = True
                if checks_failed:
                    break

            # Deal with a check failure
            if checks_failed and c is not None:
                to_send_failure_message = c.fail_message
                if c.on_failure == Check.failures.RETRY:
                    continue
                elif c.on_failure == Check.failures.FAIL:
                    raise ConverterFailure()
                return None  # We shouldn't reach here but this is just for good luck

            # And we converted properly
            return await self.converter.convert(
                ctx,
                modal_submission.components[0].components[0].value,
            )
