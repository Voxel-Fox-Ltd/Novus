from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Dict, Protocol, Union, Type, Optional, List, overload

import discord
from discord.ext import commands

from .check import Check, ModalCheck
from .errors import ConverterFailure, ConverterTimeout
from .utils import get_discord_converter

if TYPE_CHECKING:
    TypeConverter = Union[
        Type[discord.Role],
        Type[discord.TextChannel],
        Type[discord.User],
        Type[discord.Member],
        Type[discord.VoiceChannel],
        Type[str],
        Type[int],
        Type[bool],
    ]
    AnyConverter = Union[
        Callable[[discord.Interaction], bool],
        TypeConverter,
    ]


class _ConverterProtocol(Protocol):
    callback: Callable
    async def convert(self, ctx, value): ...


class _FakeConverter(object):

    def __init__(self, callback):
        self.callback = callback

    async def convert(self, ctx, value):
        return self.callback(value)


class Converter(object):
    """
    An object for use in the settings menus for describing things that the user should input.
    """

    @overload
    def __init__(
            self,
            prompt: str,
            checks: Optional[List[Check]] = ...,
            converter: Optional[Callable[[discord.Interaction], bool]] = ...,
            components: discord.ui.MessageComponents = ...,
            timeout_message: Optional[str] = ...,
            input_text_kwargs: Optional[Dict[str, Any]] = None):
        ...

    @overload
    def __init__(
            self,
            prompt: str,
            checks: Optional[List[Check]] = ...,
            converter: Optional[TypeConverter] = ...,
            components: Optional[discord.ui.MessageComponents] = None,
            timeout_message: Optional[str] = ...,
            input_text_kwargs: Optional[Dict[str, Any]] = None):
        ...

    def __init__(
            self,
            prompt: str,
            checks: Optional[List[Check]] = None,
            converter: Optional[AnyConverter] = str,
            components: Optional[discord.ui.MessageComponents] = None,
            timeout_message: Optional[str] = None,
            input_text_kwargs: Optional[Dict[str, Any]] = None):
        """
        Parameters
        ----------
        prompt : str
            The message that should be sent to the user when asking
            for the convertable.
        checks : Optional[Optional[List[Check]]]
            A list of check objects that should be used to make sure the user's
            input is valid. These will be silently ignored if a :code:`components` parameter is passed.
        converter : Optional[Optional[AnyConverter]]
            A callable that
            will be used to convert the user's input. If a converter fails
            then :code:`None` will be returned, so use the given checks
            to make sure that this does not happen if this behaviour
            is undesirable. If you set :code:`components`, then this
            function should instead take the payload instance that was
            given back by the user's interaction.
        components : Optional[Optional[discord.ui.MessageComponents]]
            An instance of message components to be sent by the bot.
            If components are sent then the bot will not accept a message as a response, only an interaction
            with the component.
        timeout_message : Optional[Optional[str]]
            The message that should get output to the user if this converter times out.
        input_text_kwargs : Optional[Optional[Dict[str, Any]]]
            Kwargs to be passed directly into the InputText for the modal.
        """

        self.prompt: str = prompt
        self.checks: List[Check] = checks or list()
        self._converter: Optional[AnyConverter] = converter
        self.converter: _ConverterProtocol = self._wrap_converter(converter)  # type: ignore - reassignment
        self.components: Optional[discord.ui.MessageComponents] = components
        self.timeout_message: Optional[str] = timeout_message
        self.input_text_kwargs: Dict[str, Any] = input_text_kwargs or dict()

    @staticmethod
    def _wrap_converter(converter: AnyConverter):
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
            return await self._run_with_components(ctx, messages_to_delete)

        # The input is a modal - branch off here
        try:
            return await self._run_with_modal(ctx, messages_to_delete)
        except Exception as e:
            ctx.bot.logger.error("asdada", exc_info=e)
            raise

    async def _run_with_components(
            self,
            ctx: commands.SlashContext,
            messages_to_delete: List[discord.Message]):
        """
        Run this converter when this components have been supplied.
        """

        # We got components baby
        assert isinstance(self.components, discord.ui.MessageComponents)

        # Get the valid custom IDs
        valid_ids = []
        for action_row in self.components.components:
            for interactable in action_row.components:
                valid_ids.append(interactable.custom_id)

        # Send message to respond to
        sent_message = None
        if ctx.interaction.response.is_done:
            sent_message = await ctx.interaction.followup.send(
                self.prompt,
                components=self.components,
            )
            if sent_message:
                messages_to_delete.append(sent_message)
        else:
            await ctx.interaction.response.edit_message(
                content=self.prompt,
                components=self.components,
            )

        # Set up checks
        def button_check(payload: discord.Interaction):
            if payload.custom_id not in valid_ids:
                return False
            if payload.user.id == ctx.interaction.user.id:
                return True
            ctx.bot.loop.create_task(payload.response.send_message(
                f"Only {ctx.interaction.user.mention} can interact with these buttons.",
                ephemeral=True,
            ))
            return False

        # Wait for the user to click a button
        try:
            payload = await ctx.bot.wait_for(
                "component_interaction",
                check=button_check,
                timeout=60.0,
            )
            ctx.interaction = payload
            await payload.response.defer_update()
        except asyncio.TimeoutError:
            raise ConverterTimeout(self.timeout_message)

        # And convert
        return await self.converter.convert(ctx, payload)

    async def _run_with_modal(
            self,
            ctx: commands.SlashContext,
            messages_to_delete: List[discord.Message]):
        """
        Run this converter when this no components are supplied - spawn a modal.
        """

        # Set up a button for them to click that spawns a modal
        button = discord.ui.Button(label="Input")
        cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        components = discord.ui.MessageComponents.add_buttons_with_rows(button, cancel)
        to_send_failure_message = None

        # Send the button
        sent_message = None
        if ctx.interaction.response.is_done:
            await ctx.interaction.edit_original_message(
                content=to_send_failure_message or self.prompt,
                embeds=[],
                components=components,
            )
            if sent_message:
                messages_to_delete.append(sent_message)
        else:
            await ctx.interaction.response.edit_message(
                content=to_send_failure_message or self.prompt,
                embeds=[],
                components=components,
            )

        # Loop until a valid input is received
        running_modal_task: Optional[asyncio.Task] = None
        while True:

            # Set up our wait for the button click
            wait_tasks: List[Union[asyncio.Task, asyncio.Future]] = [
                ctx.bot.wait_for(
                    "component_interaction",
                    check=lambda i: (
                        i.user.id == ctx.interaction.user.id and
                        i.custom_id in [button.custom_id, cancel.custom_id]
                    ),
                ),
            ]

            # Set up our wait for the modal submit, if there is one
            if running_modal_task and not running_modal_task.done():
                wait_tasks.append(running_modal_task)

            # Wait for one of those things to happen
            done, pending = await asyncio.wait(wait_tasks, return_when=asyncio.FIRST_COMPLETED)

            # Cancel waiting for the other task
            for t in pending:
                t.cancel()

            # Get the result from the task
            result = None
            for t in done:
                result = t.result()
            assert result

            # See what the task is; if it's an interaction then we gotta spawn
            # a new modal
            if isinstance(result, discord.Interaction):
                if running_modal_task:
                    running_modal_task.cancel()
                ctx.interaction = result  # Don't defer this one so we can send a modal
                if ctx.interaction.custom_id == cancel.custom_id:
                    return None
                running_modal_task = ctx.bot.loop.create_task(self._run_spawn_modal(ctx))
                continue

            # If it's anything else, it'll be from the modal task
            if isinstance(result, Check):
                to_send_failure_message = result.fail_message
                await ctx.interaction.followup.send(
                    to_send_failure_message or self.prompt,
                    ephemeral=True,
                )
                continue
            elif isinstance(result, commands.CommandError):
                to_send_failure_message = str(result)
                await ctx.interaction.followup.send(
                    to_send_failure_message or self.prompt,
                    ephemeral=True,
                )
                continue

            # And if it's anything other than a check then everything
            # is fine
            return result

    async def _run_spawn_modal(
            self,
            ctx: commands.SlashContext) -> Union[Check, Any]:
        """
        Spawn a modal from the button click.

        Parameters
        ----------
        ctx : commands.SlashContext
            The context that brought us to this moment.

        Returns
        -------
        Union[Check, Any]
            Either the check that failed, in the case of a check failure,
            of the returned response. Could be ``None``.

        Raises
        ------
        ConverterFailure
            If the conversion failed and we aren't prompted
            to retry.
        """

        # Send the user a modal
        modal = discord.ui.Modal(
            title="Menu Data",
            components=[
                discord.ui.ActionRow(
                    discord.ui.InputText(
                        label="Input",
                        **self.input_text_kwargs,
                    ),
                ),
            ],
        )
        await ctx.interaction.response.send_modal(modal)

        # Wait for an input
        modal_submission: discord.Interaction = await ctx.bot.wait_for(
            "modal_submit",
            check=lambda i: i.user.id == ctx.interaction.user.id and i.custom_id == modal.custom_id,
            timeout=60.0 * 30,
        )
        ctx.interaction = modal_submission
        await ctx.interaction.response.defer_update()  # Defer so we can run our checks

        # Run it through our checks
        checks_failed = False
        c = None
        for c in self.checks:
            try:
                assert isinstance(c, ModalCheck), "Check is not a modal check"
                checks_failed = not c.check(modal_submission)
            except AssertionError as e:
                ctx.bot.logger.error("Error in menus in check", exc_info=e)
                checks_failed = True
            except Exception as e:
                checks_failed = True
            if checks_failed:
                break

        # Deal with a check failure
        if checks_failed and c is not None:
            return c

        # And we converted properly
        try:
            return await self.converter.convert(
                ctx,
                modal_submission.components[0].components[0].value,
            )
        except commands.CommandError as e:
            return e
