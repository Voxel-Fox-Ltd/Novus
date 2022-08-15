"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    Literal,
    List,
    Optional,
    Union,
    Set,
    Tuple,
    TypeVar,
    Type,
    TYPE_CHECKING,
    overload,
    get_args,
)
import asyncio
import functools
import inspect
import datetime

import discord

from .errors import *
from .cooldowns import Cooldown, BucketType, CooldownMapping, MaxConcurrency, DynamicCooldownMapping
from .converter import run_converters, get_converter, Greedy
from ._types import _BaseCommand
from .cog import Cog
from .context import Context, SlashContext
from ...enums import Locale


if TYPE_CHECKING:
    from typing_extensions import Concatenate, ParamSpec, TypeGuard

    from discord.message import Message

    from ._types import (
        Coro,
        CoroFunc,
        Check,
        Hook,
        Error,
        Autocomplete,
    )


__all__ = (
    'ApplicationCommandMeta',
    'Command',
    'ContextMenuCommand',
    'Group',
    'GroupMixin',
    'command',
    'context_command',
    'group',
    'has_role',
    'has_permissions',
    'has_any_role',
    'check',
    'check_any',
    'before_invoke',
    'after_invoke',
    'bot_has_role',
    'bot_has_permissions',
    'bot_has_any_role',
    'cooldown',
    'dynamic_cooldown',
    'max_concurrency',
    'dm_only',
    'guild_only',
    'is_owner',
    'is_nsfw',
    'has_guild_permissions',
    'bot_has_guild_permissions',
    'defer',
    'is_slash_command',
)

MISSING: Any = discord.utils.MISSING

T = TypeVar('T')
CogT = TypeVar('CogT', bound='Cog')
CommandT = TypeVar('CommandT', bound='Command')
ContextT = TypeVar('ContextT', bound='Context')
# CHT = TypeVar('CHT', bound='Check')
GroupT = TypeVar('GroupT', bound='Group')
HookT = TypeVar('HookT', bound='Hook')
ErrorT = TypeVar('ErrorT', bound='Error')
AutocompleteT = TypeVar('AutocompleteT', bound='Autocomplete')

if TYPE_CHECKING:
    P = ParamSpec('P')
else:
    P = TypeVar('P')


SLASH_PERMISSION_IGNORES = [
    'send_messages',
    'embed_links',
    'attach_files',
    'external_emojis',
    'read_messages',
]  # permissions that don't matter to slash command checks


def unwrap_function(function: Callable[..., Any]) -> Callable[..., Any]:
    partial = functools.partial
    while True:
        if hasattr(function, '__wrapped__'):
            function = function.__wrapped__
        elif isinstance(function, partial):
            function = function.func
        else:
            return function


def get_signature_parameters(function: Callable[..., Any], globalns: Dict[str, Any]) -> Dict[str, inspect.Parameter]:
    signature = inspect.signature(function)
    params = {}
    cache: Dict[str, Any] = {}
    eval_annotation = discord.utils.evaluate_annotation
    for name, parameter in signature.parameters.items():
        annotation = parameter.annotation
        if annotation is parameter.empty:
            params[name] = parameter
            continue
        if annotation is None:
            params[name] = parameter.replace(annotation=type(None))
            continue

        annotation = eval_annotation(annotation, globalns, globalns, cache)
        if annotation is Greedy:
            raise TypeError('Unparameterized Greedy[...] is disallowed in signature.')

        params[name] = parameter.replace(annotation=annotation)

    return params


def wrap_callback(coro):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)
        except CommandError:
            raise
        except asyncio.CancelledError:
            return
        except Exception as exc:
            raise CommandInvokeError(exc) from exc
        return ret
    return wrapped


def hooked_wrapped_callback(command, ctx, coro):
    @functools.wraps(coro)
    async def wrapped(*args, **kwargs):
        try:
            ret = await coro(*args, **kwargs)
        except CommandError:
            ctx.command_failed = True
            raise
        except asyncio.CancelledError:
            ctx.command_failed = True
            return
        except Exception as exc:
            ctx.command_failed = True
            raise CommandInvokeError(exc) from exc
        finally:
            if command._max_concurrency is not None:
                await command._max_concurrency.release(ctx)

            await command.call_after_hooks(ctx)
        return ret
    return wrapped


class _CaseInsensitiveDict(dict):
    def __contains__(self, k):
        return super().__contains__(k.casefold())

    def __delitem__(self, k):
        return super().__delitem__(k.casefold())

    def __getitem__(self, k):
        return super().__getitem__(k.casefold())

    def get(self, k, default=None):
        return super().get(k.casefold(), default)

    def pop(self, k, default=None):
        return super().pop(k.casefold(), default)

    def __setitem__(self, k, v):
        super().__setitem__(k.casefold(), v)


class ApplicationCommandMeta:
    """
    A container class for passing information about application commands
    onto a command decorator, so that automatic conversion between text
    commands and slash commands works without a hitch.

    This is used instead of using :class:`discord.ApplicationCommand` so that
    you don't need to do a bunch of funky stuff to get command groups to work.

    .. versionadded:: 0.0.6
    """

    def __init__(
            self,
            *,
            options: Optional[List[discord.ApplicationCommandOption]] = None,
            name_localizations: Optional[Dict[Union[Locale, str], str]] = None,
            description_localizations: Optional[Dict[Union[Locale, str], str]] = None,
            guild_only: bool = False,
            permissions: Optional[discord.Permissions] = None
            ):
        """
        Parameters
        ----------
        options : Optional[List[discord.ApplicationCommandOption]]
            The data for the parameters that should be converted into an application
            command.
        name_localizations : Optional[Dict[str, str]]
            A dictionary of language: text translations for the name of the command.
        description_localizations : Optional[Dict[str, str]]
            A dictionary of language: text translations for the description of the command.
        guild_only : Optional[bool]
            Whether or not the command is only runnable in a guild.
        permissions : Optional[discord.Permissions]
            The permissions required by default to run the command.
        """

        self.options: List[discord.ApplicationCommandOption] = options or list()
        self.name_localizations: Dict[Union[Locale, str], str] = name_localizations or dict()
        self.description_localizations: Dict[Union[Locale, str], str] = description_localizations or dict()
        self.guild_only: bool = guild_only
        self.permissions: Optional[discord.Permissions] = permissions


class Command(_BaseCommand, Generic[CogT, P, T]):
    r"""A class that implements the protocol for a bot text command.

    These are not created manually, instead they are created via the
    decorator or functional interface.

    Attributes
    -----------
    name: :class:`str`
        The name of the command.
    callback: :ref:`coroutine <coroutine>`
        The coroutine that is executed when the command is called.
    help: Optional[:class:`str`]
        The long help text for the command.
    brief: Optional[:class:`str`]
        The short help text for the command.
    usage: Optional[:class:`str`]
        A replacement for arguments in the default help text.
    aliases: Union[List[:class:`str`], Tuple[:class:`str`]]
        The list of aliases the command can be invoked under.
    enabled: :class:`bool`
        A boolean that indicates if the command is currently enabled.
        If the command is invoked while it is disabled, then
        :exc:`.DisabledCommand` is raised to the :func:`.on_command_error`
        event. Defaults to ``True``.
    parent: Optional[:class:`Group`]
        The parent group that this command belongs to. ``None`` if there
        isn't one.
    cog: Optional[:class:`Cog`]
        The cog that this command belongs to. ``None`` if there isn't one.
    checks: List[Callable[[:class:`.Context`], :class:`bool`]]
        A list of predicates that verifies if the command could be executed
        with the given :class:`.Context` as the sole parameter. If an exception
        is necessary to be thrown to signal failure, then one inherited from
        :exc:`.CommandError` should be used. Note that if the checks fail then
        :exc:`.CheckFailure` exception is raised to the :func:`.on_command_error`
        event.
    description: :class:`str`
        The message prefixed into the default help command.
    hidden: :class:`bool`
        If ``True``\, the default help command does not show this in the
        help output.
    rest_is_raw: :class:`bool`
        If ``False`` and a keyword-only argument is provided then the keyword
        only argument is stripped and handled as if it was a regular argument
        that handles :exc:`.MissingRequiredArgument` and default values in a
        regular matter rather than passing the rest completely raw. If ``True``
        then the keyword-only argument will pass in the rest of the arguments
        in a completely raw matter. Defaults to ``False``.
    invoked_subcommand: Optional[:class:`Command`]
        The subcommand that was invoked, if any.
    require_var_positional: :class:`bool`
        If ``True`` and a variadic positional argument is specified, requires
        the user to specify at least one argument. Defaults to ``False``.
    ignore_extra: :class:`bool`
        If ``True``\, ignores extraneous strings passed to a command if all its
        requirements are met (e.g. ``?foo a b c`` when only expecting ``a``
        and ``b``). Otherwise :func:`.on_command_error` and local error handlers
        are called with :exc:`.TooManyArguments`. Defaults to ``True``.
    cooldown_after_parsing: :class:`bool`
        If ``True``\, cooldown processing is done after argument parsing,
        which calls converters. If ``False`` then cooldown processing is done
        first and then the converters are called second. Defaults to ``False``.
    extras: :class:`dict`
        A dict of user provided extras to attach to the Command.

        .. note::
            This object may be copied by the library.
    application_command_meta: :class:`ApplicationCommandMeta`
        Additional information for the command to be passed to the application
        command. Only commands with a meta object set will work with
        :func:`Bot.register_application_commands`.

        .. versionadded:: 0.0.6
    """

    __original_kwargs__: Dict[str, Any]

    def __new__(cls: Type[CommandT], *args: Any, **kwargs: Any) -> CommandT:
        # if you're wondering why this is done, it's because we need to ensure
        # we have a complete original copy of **kwargs even for classes that
        # mess with it by popping before delegating to the subclass __init__.
        # In order to do this, we need to control the instance creation and
        # inject the original kwargs through __new__ rather than doing it
        # inside __init__.
        self = super().__new__(cls)

        # we do a shallow copy because it's probably the most common use case.
        # this could potentially break if someone modifies a list or something
        # while it's in movement, but for now this is the cheapest and
        # fastest way to do what we want.
        self.__original_kwargs__ = kwargs.copy()
        return self

    def __init__(self, func: Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ], **kwargs: Any):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')

        name = kwargs.get('name') or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')
        self.name: str = name

        self.callback = func
        self.enabled: bool = kwargs.get('enabled', True)

        self.application_command_meta: ApplicationCommandMeta = kwargs.get("application_command_meta", None)

        help_doc = kwargs.get('help')
        if help_doc is not None:
            help_doc = inspect.cleandoc(help_doc)
        else:
            help_doc = inspect.getdoc(func)
            if isinstance(help_doc, bytes):
                help_doc = help_doc.decode('utf-8')

        self.help: Optional[str] = help_doc

        self.brief: Optional[str] = kwargs.get('brief')
        self.usage: Optional[str] = kwargs.get('usage')
        self.rest_is_raw: bool = kwargs.get('rest_is_raw', False)
        self.aliases: Union[List[str], Tuple[str]] = kwargs.get('aliases', [])
        self.extras: Dict[str, Any] = kwargs.get('extras', {})

        if not isinstance(self.aliases, (list, tuple)):
            raise TypeError("Aliases of a command must be a list or a tuple of strings.")

        self.description: str = inspect.cleandoc(kwargs.get('description', ''))
        self.hidden: bool = kwargs.get('hidden', False)

        try:
            checks = func.__commands_checks__
            checks.reverse()
        except AttributeError:
            checks = kwargs.get('checks', [])

        self.checks: List[Check] = checks

        try:
            cooldown = func.__commands_cooldown__
        except AttributeError:
            cooldown = kwargs.get('cooldown')

        if cooldown is None:
            buckets = CooldownMapping(cooldown, BucketType.default)
        elif isinstance(cooldown, CooldownMapping):
            buckets = cooldown
        else:
            raise TypeError("Cooldown must be a an instance of CooldownMapping or None.")
        self._buckets: CooldownMapping = buckets

        try:
            max_concurrency = func.__commands_max_concurrency__
        except AttributeError:
            max_concurrency = kwargs.get('max_concurrency')

        self._max_concurrency: Optional[MaxConcurrency] = max_concurrency

        self.require_var_positional: bool = kwargs.get('require_var_positional', False)
        self.ignore_extra: bool = kwargs.get('ignore_extra', True)
        self.cooldown_after_parsing: bool = kwargs.get('cooldown_after_parsing', False)
        self.cog: Optional[CogT] = None

        # bandaid for the fact that sometimes parent can be the bot instance
        parent = kwargs.get('parent')
        self.parent: Optional[GroupMixin] = parent if isinstance(parent, _BaseCommand) else None  # type: ignore

        self._before_invoke: Optional[Hook] = None
        try:
            before_invoke = func.__before_invoke__
        except AttributeError:
            pass
        else:
            self.before_invoke(before_invoke)

        self._after_invoke: Optional[Hook] = None
        try:
            after_invoke = func.__after_invoke__
        except AttributeError:
            pass
        else:
            self.after_invoke(after_invoke)

    @property
    def callback(self) -> Union[
            Callable[Concatenate[CogT, Context, P], Coro[T]],
            Callable[Concatenate[Context, P], Coro[T]],
        ]:
        return self._callback

    @callback.setter
    def callback(self, function: Union[
            Callable[Concatenate[CogT, Context, P], Coro[T]],
            Callable[Concatenate[Context, P], Coro[T]],
        ]) -> None:
        self._callback = function
        unwrap = unwrap_function(function)
        self.module = unwrap.__module__

        try:
            globalns = unwrap.__globals__
        except AttributeError:
            globalns = {}

        self.params = get_signature_parameters(function, globalns)

    def add_check(self, func: Check) -> None:
        """Adds a check to the command.

        This is the non-decorator interface to :func:`.check`.

        Parameters
        -----------
        func
            The function that will be used as a check.
        """

        self.checks.append(func)

    def remove_check(self, func: Check) -> None:
        """Removes a check from the command.

        This function is idempotent and will not raise an exception
        if the function is not in the command's checks.

        Parameters
        -----------
        func
            The function to remove from the checks.
        """

        try:
            self.checks.remove(func)
        except ValueError:
            pass

    def update(self, **kwargs: Any) -> None:
        """Updates :class:`Command` instance with updated attribute.

        This works similarly to the :func:`.command` decorator in terms
        of parameters in that they are passed to the :class:`Command` or
        subclass constructors, sans the name and callback.
        """
        self.__init__(self.callback, **dict(self.__original_kwargs__, **kwargs))

    async def __call__(self, context: Context, *args: P.args, **kwargs: P.kwargs) -> T:
        """|coro|

        Calls the internal callback that the command holds.

        .. note::

            This bypasses all mechanisms -- including checks, converters,
            invoke hooks, cooldowns, etc. You must take care to pass
            the proper arguments and types to this function.
        """
        if self.cog is not None:
            return await self.callback(self.cog, context, *args, **kwargs)  # type: ignore
        else:
            return await self.callback(context, *args, **kwargs)  # type: ignore

    def _ensure_assignment_on_copy(self, other: CommandT) -> CommandT:
        other._before_invoke = self._before_invoke
        other._after_invoke = self._after_invoke
        if self.checks != other.checks:
            other.checks = self.checks.copy()
        if self._buckets.valid and not other._buckets.valid:
            other._buckets = self._buckets.copy()
        if self._max_concurrency != other._max_concurrency:
            # _max_concurrency won't be None at this point
            other._max_concurrency = self._max_concurrency.copy()  # type: ignore

        try:
            other.on_error = self.on_error
        except AttributeError:
            pass
        try:
            other.on_autocomplete = self.on_autocomplete
        except AttributeError:
            pass
        return other

    def copy(self: CommandT) -> CommandT:
        """Creates a copy of this command.

        Returns
        --------
        :class:`Command`
            A new instance of this command.
        """
        ret = self.__class__(self.callback, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)

    def _update_copy(self: CommandT, kwargs: Dict[str, Any]) -> CommandT:
        if kwargs:
            kw = kwargs.copy()
            kw.update(self.__original_kwargs__)
            copy = self.__class__(self.callback, **kw)
            return self._ensure_assignment_on_copy(copy)
        else:
            return self.copy()

    async def dispatch_error(self, ctx: Context, error: Exception) -> None:
        ctx.command_failed = True
        cog = self.cog
        try:
            coro = self.on_error
        except AttributeError:
            pass
        else:
            injected = wrap_callback(coro)
            if cog is not None:
                await injected(cog, ctx, error)
            else:
                await injected(ctx, error)

        try:
            if cog is not None:
                local = Cog._get_overridden_method(cog.cog_command_error)
                if local is not None:
                    wrapped = wrap_callback(local)
                    await wrapped(ctx, error)
        finally:
            ctx.bot.dispatch('command_error', ctx, error)

    async def dispatch_autocomplete(self, ctx: Context, interaction) -> None:
        cog = self.cog
        try:
            coro = self.on_autocomplete
        except AttributeError:
            pass
        else:
            try:
                injected = wrap_callback(coro)
                if cog is not None:
                    await injected(cog, ctx, interaction)
                else:
                    await injected(ctx, interaction)
            except Exception:
                pass

    async def transform(self, ctx: Context, param: inspect.Parameter) -> Any:
        required = param.default is param.empty
        converter = get_converter(param)
        consume_rest_is_special = param.kind == param.KEYWORD_ONLY and not self.rest_is_raw
        view = None
        if hasattr(ctx, "view"):
            view = ctx.view
            view.skip_ws()

        # The greedy converter is simple -- it keeps going until it fails in which case,
        # it undos the view ready for the next parameter to use instead
        # Greedy isn't something we need to worry about when it comes to slash commands,
        # since the lib just errors by default when adding them.
        if view and isinstance(converter, Greedy):
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
                return await self._transform_greedy_pos(ctx, param, required, converter.converter)
            elif param.kind == param.VAR_POSITIONAL:
                return await self._transform_greedy_var_pos(ctx, param, converter.converter)
            else:
                # if we're here, then it's a KEYWORD_ONLY param type
                # since this is mostly useless, we'll helpfully transform Greedy[X]
                # into just X and do the parsing that way.
                converter = converter.converter

        # Seeing if we're at the end of the given values via eof, or if the name
        # given isn't in the params returned by Discord in the case of slashies
        if (view and view.eof) or (getattr(ctx, "given_values", None) is not None and param.name not in getattr(ctx, "given_values", {})):
            if param.kind == param.VAR_POSITIONAL:
                raise RuntimeError() # break the loop
            if required:
                if self._is_typing_optional(param.annotation):
                    return None
                if hasattr(converter, '__commands_is_flag__') and converter._can_be_constructible():
                    return await converter._construct_default(ctx)
                raise MissingRequiredArgument(param)
            return param.default

        # Set a fallback for the text commands so we can go back later
        previous = -1
        if view:
            previous = view.index

        # See if we want to consume the rest of the argument from the view,
        # from which we can just grab all remaining content
        if consume_rest_is_special:
            if view:
                argument = view.read_rest().strip()
            else:
                argument = getattr(ctx, "given_values", {}).get(param.name)  # Slash context

        # Just a normal argument that we want to grab the value of
        else:
            try:
                if view:
                    argument = view.get_quoted_word()
                else:
                    argument = getattr(ctx, "given_values", {}).get(param.name)  # Slash context
            except (KeyError, ArgumentParsingError) as exc:
                if self._is_typing_optional(param.annotation):
                    if view:
                        view.index = previous
                    return None
                else:
                    raise exc

        # Update the view so we can get the next part of text commands next runthrough
        if view:
            view.previous = previous

        # type-checker fails to narrow argument
        return await run_converters(ctx, converter, argument, param)  # type: ignore

    async def _transform_greedy_pos(self, ctx: Context, param: inspect.Parameter, required: bool, converter: Any) -> Any:
        view = ctx.view
        result = []
        while not view.eof:
            # for use with a manual undo
            previous = view.index

            view.skip_ws()
            try:
                argument = view.get_quoted_word()
                value = await run_converters(ctx, converter, argument, param)  # type: ignore
            except (CommandError, ArgumentParsingError):
                view.index = previous
                break
            else:
                result.append(value)

        if not result and not required:
            return param.default
        return result

    async def _transform_greedy_var_pos(self, ctx: Context, param: inspect.Parameter, converter: Any) -> Any:
        view = ctx.view
        previous = view.index
        try:
            argument = view.get_quoted_word()
            value = await run_converters(ctx, converter, argument, param)  # type: ignore
        except (CommandError, ArgumentParsingError):
            view.index = previous
            raise RuntimeError() from None # break loop
        else:
            return value

    @property
    def clean_params(self) -> Dict[str, inspect.Parameter]:
        """Dict[:class:`str`, :class:`inspect.Parameter`]:
        Retrieves the parameter dictionary without the context or self parameters.

        Useful for inspecting signature.
        """
        result = self.params.copy()
        if self.cog is not None:
            # first parameter is self
            try:
                del result[next(iter(result))]
            except StopIteration:
                raise ValueError("missing 'self' parameter") from None

        try:
            # first/second parameter is context
            del result[next(iter(result))]
        except StopIteration:
            raise ValueError("missing 'context' parameter") from None

        return result

    @property
    def full_parent_name(self) -> str:
        """:class:`str`: Retrieves the fully qualified parent command name.

        This the base command name required to execute it. For example,
        in ``?one two three`` the parent name would be ``one two``.
        """
        entries = []
        command = self
        # command.parent is type-hinted as GroupMixin some attributes are resolved via MRO
        while command.parent is not None: # type: ignore
            command = command.parent # type: ignore
            entries.append(command.name) # type: ignore

        return ' '.join(reversed(entries))

    @property
    def parents(self) -> List[Group]:
        """List[:class:`Group`]: Retrieves the parents of this command.

        If the command has no parents then it returns an empty :class:`list`.

        For example in commands ``?a b c test``, the parents are ``[c, b, a]``.
        """
        entries = []
        command = self
        while command.parent is not None: # type: ignore
            command = command.parent # type: ignore
            entries.append(command)

        return entries

    @property
    def root_parent(self) -> Optional[Group]:
        """Optional[:class:`Group`]: Retrieves the root parent of this command.

        If the command has no parents then it returns ``None``.

        For example in commands ``?a b c test``, the root parent is ``a``.
        """
        if not self.parent:
            return None
        return self.parents[-1]

    @property
    def qualified_name(self) -> str:
        """:class:`str`: Retrieves the fully qualified command name.

        This is the full parent name with the command name as well.
        For example, in ``?one two three`` the qualified name would be
        ``one two three``.
        """

        parent = self.full_parent_name
        if parent:
            return parent + ' ' + self.name
        else:
            return self.name

    def __str__(self) -> str:
        return self.qualified_name

    async def _parse_arguments(self, ctx: Context) -> None:
        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        view = None
        if hasattr(ctx, "view"):
            view = ctx.view
        iterator = iter(self.params.items())

        if self.cog is not None:
            # we have 'self' as the first parameter so just advance
            # the iterator and resume parsing
            try:
                next(iterator)
            except StopIteration:
                raise discord.ClientException(f'Callback for {self.name} command is missing "self" parameter.')

        # next we have the 'ctx' as the next parameter
        try:
            next(iterator)
        except StopIteration:
            raise discord.ClientException(f'Callback for {self.name} command is missing "ctx" parameter.')

        for name, param in iterator:
            ctx.current_parameter = param
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
                transformed = await self.transform(ctx, param)
                args.append(transformed)
            elif param.kind == param.KEYWORD_ONLY:
                # kwarg only param denotes "consume rest" semantics
                if self.rest_is_raw:
                    converter = get_converter(param)
                    if view:
                        argument = view.read_rest()
                    else:
                        argument = getattr(ctx, "given_values", {}).get(param.name, "")
                    kwargs[name] = await run_converters(ctx, converter, argument, param)
                else:
                    kwargs[name] = await self.transform(ctx, param)
                break
            elif param.kind == param.VAR_POSITIONAL:
                if view:
                    if view.eof and self.require_var_positional:
                        raise MissingRequiredArgument(param)
                    while not view.eof:
                        try:
                            transformed = await self.transform(ctx, param)
                            args.append(transformed)
                        except RuntimeError:
                            break
                else:
                    raise discord.ClientException(f"Callback for {self.name} cannot handle variable-length args in slash commands.")

        if view and not self.ignore_extra and not view.eof:
            raise TooManyArguments('Too many arguments passed to ' + self.qualified_name)

    async def call_before_hooks(self, ctx: Context) -> None:
        # now that we're done preparing we can call the pre-command hooks
        # first, call the command local hook:
        cog = self.cog
        if self._before_invoke is not None:
            # should be cog if @commands.before_invoke is used
            instance = getattr(self._before_invoke, '__self__', cog)
            # __self__ only exists for methods, not functions
            # however, if @command.before_invoke is used, it will be a function
            if instance:
                await self._before_invoke(instance, ctx)  # type: ignore
            else:
                await self._before_invoke(ctx)  # type: ignore

        # call the cog local hook if applicable:
        if cog is not None:
            hook = Cog._get_overridden_method(cog.cog_before_invoke)
            if hook is not None:
                await hook(ctx)

        # call the bot global hook if necessary
        hook = ctx.bot._before_invoke
        if hook is not None:
            await hook(ctx)

    async def call_after_hooks(self, ctx: Context) -> None:
        cog = self.cog
        if self._after_invoke is not None:
            instance = getattr(self._after_invoke, '__self__', cog)
            if instance:
                await self._after_invoke(instance, ctx)  # type: ignore
            else:
                await self._after_invoke(ctx)  # type: ignore

        # call the cog local hook if applicable:
        if cog is not None:
            hook = Cog._get_overridden_method(cog.cog_after_invoke)
            if hook is not None:
                await hook(ctx)

        hook = ctx.bot._after_invoke
        if hook is not None:
            await hook(ctx)

    def _prepare_cooldowns(self, ctx: Context) -> None:
        if self._buckets.valid:
            dt = (ctx.message.edited_at or ctx.message.created_at) if ctx.message else discord.utils.snowflake_time(ctx.interaction.id)
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            bucket = self._buckets.get_bucket(self._buckets.get_message(ctx), current)
            if bucket is not None:
                retry_after = bucket.update_rate_limit(current)
                if retry_after:
                    raise CommandOnCooldown(bucket, retry_after, self._buckets.type)  # type: ignore

    async def _prepare_text(self, ctx: Context) -> None:
        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure(f'The check functions for command {self.qualified_name} failed.')

        if self._max_concurrency is not None:
            # For this application, context can be duck-typed as a Message
            await self._max_concurrency.acquire(ctx)  # type: ignore

        try:
            if self.cooldown_after_parsing:
                await self._parse_arguments(ctx)
                self._prepare_cooldowns(ctx)
            else:
                self._prepare_cooldowns(ctx)
                await self._parse_arguments(ctx)

            await self.call_before_hooks(ctx)
        except:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)  # type: ignore
            raise

    async def _prepare_slash(self, ctx: SlashContext) -> None:
        ctx.command = self

        if not await self.can_run(ctx):
            raise CheckFailure(f'The check functions for command {self.qualified_name} failed.')

        if self._max_concurrency is not None:
            # For this application, context can be duck-typed as a Message
            await self._max_concurrency.acquire(ctx)  # type: ignore

        try:
            if self.cooldown_after_parsing:
                await self._parse_slash_arguments(ctx)
                self._prepare_cooldowns(ctx)
            else:
                self._prepare_cooldowns(ctx)
                await self._parse_slash_arguments(ctx)

            await self.call_before_hooks(ctx)
        except:
            if self._max_concurrency is not None:
                await self._max_concurrency.release(ctx)  # type: ignore
            raise

    async def _parse_slash_arguments(self, ctx: SlashContext):
        """
        Parse the arguments for a given context.
        """

        # Set up our initial values
        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]
        ctx.kwargs = {}

        # Go through each value given by the user
        for name, value in ctx.given_values.items():

            # Get the signature
            sig = None
            if name is None:  # We only get here for context commands
                for name, sig in self.clean_params.items():
                    break  # Just get the first param - deliberately shadow "name"
            else:
                sig = self.clean_params[name]
            assert sig

            # Get the converter
            converter = get_converter(sig)

            # Get the value
            if converter == discord.Attachment:
                v = ctx.interaction.resolved.attachments[int(value)]
            elif converter == discord.Member:
                v = ctx.interaction.resolved.members[int(value)]
            elif converter == discord.User:
                v = ctx.interaction.resolved.users[int(value)]
            elif converter == discord.Message:
                v = ctx.interaction.resolved.messages[int(value)]
            elif converter == discord.Role:
                v = ctx.interaction.resolved.roles[int(value)]
            elif converter in [
                        discord.VoiceChannel,
                        discord.StageChannel,
                        discord.TextChannel,
                        discord.CategoryChannel,
                        discord.StoreChannel,
                        discord.Thread,
                        discord.ForumChannel,
                    ]:
                v = ctx.interaction.resolved.channels[int(value)]
            else:
                v = await run_converters(ctx, converter, value, sig)  # Could raise; that's fine

            # And store
            ctx.kwargs[name] = v

    async def prepare(self, ctx: Context) -> None:
        if isinstance(ctx, SlashContext):
            return await self._prepare_slash(ctx)
        else:
            return await self._prepare_text(ctx)

    def is_on_cooldown(self, ctx: Context) -> bool:
        """Checks whether the command is currently on cooldown.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to use when checking the commands cooldown status.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the command is on cooldown.
        """
        if not self._buckets.valid:
            return False

        bucket = self._buckets.get_bucket(self._buckets.get_message(ctx))
        dt = (ctx.message.edited_at or ctx.message.created_at) if ctx.message else discord.utils.snowflake_time(ctx.interaction.id)
        current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        return bucket.get_tokens(current) == 0

    def reset_cooldown(self, ctx: Context) -> None:
        """Resets the cooldown on this command.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to reset the cooldown under.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(self._buckets.get_message(ctx))
            bucket.reset()

    def get_cooldown_retry_after(self, ctx: Context) -> float:
        """Retrieves the amount of seconds before this command can be tried again.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to retrieve the cooldown from.

        Returns
        --------
        :class:`float`
            The amount of time left on this command's cooldown in seconds.
            If this is ``0.0`` then the command isn't on cooldown.
        """
        if self._buckets.valid:
            bucket = self._buckets.get_bucket(self._buckets.get_message(ctx))
            dt = (ctx.message.edited_at or ctx.message.created_at) if ctx.message else discord.utils.snowflake_time(ctx.interaction.id)
            current = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
            return bucket.get_retry_after(current)

        return 0.0

    async def invoke(self, ctx: Context) -> None:
        await self.prepare(ctx)

        # terminate the invoked_subcommand chain.
        # since we're in a regular command (and not a group) then
        # the invoked subcommand is None.
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        injected = hooked_wrapped_callback(self, ctx, self.callback)
        await injected(*ctx.args, **ctx.kwargs)

    async def reinvoke(self, ctx: Context, *, call_hooks: bool = False) -> None:
        ctx.command = self
        await self._parse_arguments(ctx)

        if call_hooks:
            await self.call_before_hooks(ctx)

        ctx.invoked_subcommand = None
        try:
            await self.callback(*ctx.args, **ctx.kwargs)  # type: ignore
        except:
            ctx.command_failed = True
            raise
        finally:
            if call_hooks:
                await self.call_after_hooks(ctx)

    def error(self, coro: ErrorT) -> ErrorT:
        """A decorator that registers a coroutine as a local error handler.

        A local error handler is an :func:`.on_command_error` event limited to
        a single command. However, the :func:`.on_command_error` is still
        invoked afterwards as the catch-all.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the local error handler.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The error handler must be a coroutine.')

        self.on_error: Error = coro
        return coro

    def has_error_handler(self) -> bool:
        """:class:`bool`: Checks whether the command has an error handler registered.
        """
        return hasattr(self, 'on_error')

    def autocomplete(self, coro: AutocompleteT) -> AutocompleteT:
        """A decorator that registers a coroutine as an autocomplete handler.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the autocomplete handler.

        Raises
        -------
        :exc:`TypeError`
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The autocomplete handler must be a coroutine.')

        self.on_autocomplete: Autocomplete = coro
        return coro

    def has_autocomplete_handler(self) -> bool:
        """:class:`bool`: Checks whether the command has an autocomplete handler registered.
        """
        return hasattr(self, 'on_autocomplete')

    def before_invoke(self, coro: HookT) -> HookT:
        """A decorator that registers a coroutine as a pre-invoke hook.

        A pre-invoke hook is called directly before the command is
        called. This makes it a useful function to set up database
        connections or any type of set up required.

        This pre-invoke hook takes a sole parameter, a :class:`.Context`.

        See :meth:`.Bot.before_invoke` for more info.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the pre-invoke hook.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The pre-invoke hook must be a coroutine.')

        self._before_invoke = coro
        return coro

    def after_invoke(self, coro: HookT) -> HookT:
        """A decorator that registers a coroutine as a post-invoke hook.

        A post-invoke hook is called directly after the command is
        called. This makes it a useful function to clean-up database
        connections or any type of clean up required.

        This post-invoke hook takes a sole parameter, a :class:`.Context`.

        See :meth:`.Bot.after_invoke` for more info.

        Parameters
        -----------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register as the post-invoke hook.

        Raises
        -------
        TypeError
            The coroutine passed is not actually a coroutine.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The post-invoke hook must be a coroutine.')

        self._after_invoke = coro
        return coro

    @property
    def cog_name(self) -> Optional[str]:
        """Optional[:class:`str`]: The name of the cog this command belongs to, if any."""
        return type(self.cog).__cog_name__ if self.cog is not None else None

    @property
    def short_doc(self) -> str:
        """:class:`str`: Gets the "short" documentation of a command.

        By default, this is the :attr:`.brief` attribute.
        If that lookup leads to an empty string then the first line of the
        :attr:`.help` attribute is used instead.
        """
        if self.brief is not None:
            return self.brief
        if self.help is not None:
            return self.help.split('\n', 1)[0]
        return ''

    def _is_typing_optional(self, annotation: Union[T, Optional[T]]) -> TypeGuard[Optional[T]]:
        return getattr(annotation, '__origin__', None) is Union and type(None) in annotation.__args__  # type: ignore

    @property
    def signature(self) -> str:
        """:class:`str`: Returns a POSIX-like signature useful for help command output."""
        if self.usage is not None:
            return self.usage

        params = self.clean_params
        if not params:
            return ''

        result = []
        for name, param in params.items():
            greedy = isinstance(param.annotation, Greedy)
            optional = False  # postpone evaluation of if it's an optional argument

            # for typing.Literal[...], typing.Optional[typing.Literal[...]], and Greedy[typing.Literal[...]], the
            # parameter signature is a literal list of it's values
            annotation = param.annotation.converter if greedy else param.annotation
            origin = getattr(annotation, '__origin__', None)
            if not greedy and origin is Union:
                none_cls = type(None)
                union_args = annotation.__args__
                optional = union_args[-1] is none_cls
                if len(union_args) == 2 and optional:
                    annotation = union_args[0]
                    origin = getattr(annotation, '__origin__', None)

            if origin is Literal:
                name = '|'.join(f'"{v}"' if isinstance(v, str) else str(v) for v in annotation.__args__)
            if param.default is not param.empty:
                # We don't want None or '' to trigger the [name=value] case and instead it should
                # do [name] since [name=None] or [name=] are not exactly useful for the user.
                should_print = param.default if isinstance(param.default, str) else param.default is not None
                if should_print:
                    result.append(f'[{name}={param.default}]' if not greedy else
                                  f'[{name}={param.default}]...')
                    continue
                else:
                    result.append(f'[{name}]')

            elif param.kind == param.VAR_POSITIONAL:
                if self.require_var_positional:
                    result.append(f'<{name}...>')
                else:
                    result.append(f'[{name}...]')
            elif greedy:
                result.append(f'[{name}]...')
            elif optional:
                result.append(f'[{name}]')
            else:
                result.append(f'<{name}>')

        return ' '.join(result)

    async def can_run(self, ctx: Context) -> bool:
        """|coro|

        Checks if the command can be executed by checking all the predicates
        inside the :attr:`~Command.checks` attribute. This also checks whether the
        command is disabled.

        Parameters
        -----------
        ctx: :class:`.Context`
            The ctx of the command currently being invoked.

        Raises
        -------
        :class:`CommandError`
            Any command error that was raised during a check call will be propagated
            by this function.

        Returns
        --------
        :class:`bool`
            A boolean indicating if the command can be invoked.
        """

        if not self.enabled:
            raise DisabledCommand(f'{self.name} command is disabled')

        original = ctx.command
        ctx.command = self

        try:
            if not await ctx.bot.can_run(ctx):
                raise CheckFailure(f'The global check functions for command {self.qualified_name} failed.')

            cog = self.cog
            if cog is not None:
                local_check = Cog._get_overridden_method(cog.cog_check)
                if local_check is not None:
                    ret = await discord.utils.maybe_coroutine(local_check, ctx)
                    if not ret:
                        return False

            predicates = self.checks
            if not predicates:
                # since we have no checks, then we just return True.
                return True

            return await discord.utils.async_all(predicate(ctx) for predicate in predicates)  # type: ignore
        finally:
            ctx.command = original

    def to_application_command(self) -> Union[discord.ApplicationCommand, discord.ApplicationCommandOption]:
        """Convert the current command instance to an application command.

        Returns
        --------
        Union[:class:`discord.ApplicationCommand`, :class:`discord.ApplicationCommandOption`]
            An application command equivelant to the current command instance.
        """

        # Get the localizations
        if self.application_command_meta is None and self.clean_params:
            raise TypeError(f"Missing application command meta in command {self.name}.")
        elif self.application_command_meta is None:
            name_localizations = None
            description_localizations = None
            default_member_permissions = None
            guild_only = None
        else:
            name_localizations = self.application_command_meta.name_localizations
            description_localizations = self.application_command_meta.description_localizations
            default_member_permissions = self.application_command_meta.permissions
            guild_only = self.application_command_meta.guild_only

        # Create the base command
        if self.parent is None:  # No parent
            command = discord.ApplicationCommand(
                name=self.name,
                type=discord.ApplicationCommandType.chat_input,
                description=self.short_doc or self.name,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
                default_member_permissions=default_member_permissions,
                dm_permissions=not guild_only,
            )
        else:  # Parent is a group
            command = discord.ApplicationCommandOption(
                name=self.name,
                type=discord.ApplicationCommandOptionType.subcommand,
                description=self.short_doc or self.name,
                name_localizations=name_localizations,
                description_localizations=description_localizations,
            )

        # If we don't have a meta
        if self.application_command_meta is None:
            return command

        # Add arguments if we set up a meta
        for option in self.application_command_meta.options:
            command.add_option(option)
        return command


class ContextMenuCommand(Command):
    """The base command class for context menu commands.

    .. versionadded:: 0.0.3
    """

    @property
    def callback(self) -> Union[
            Callable[Concatenate[CogT, Context, P], Coro[T]],
            Callable[Concatenate[Context, P], Coro[T]],
        ]:
        return self._callback

    @callback.setter
    def callback(self, function: Union[
            Callable[Concatenate[CogT, Context, P], Coro[T]],
            Callable[Concatenate[Context, P], Coro[T]],
        ]) -> None:
        self._callback = function
        unwrap = unwrap_function(function)
        self.module = unwrap.__module__

        try:
            globalns = unwrap.__globals__
        except AttributeError:
            globalns = {}

        self.params = get_signature_parameters(function, globalns)

        # Some checks to make sure the context command is valid,
        # as well as to interpret its typing
        if len(self.params) not in [1, 3]:
            raise ValueError("Context menu commands can have exactly one parameter.")
        has_cog = len(self.params) == 3
        for index, (_, type_) in enumerate(self.params.items()):
            if has_cog and index < 2:
                continue
            if not (annotation := type_.annotation):
                raise ValueError("Missing annotation for interpolated context menu command.")

            base_annotations = get_args(annotation)
            if not base_annotations:
                base_annotations = (annotation,)
            mro = []
            for i in base_annotations:
                mro.extend(i.mro())

            if discord.Message in mro:
                self.application_command_type = discord.ApplicationCommandType.message
            elif discord.user._UserTag in mro:
                self.application_command_type = discord.ApplicationCommandType.user
            else:
                raise TypeError("Invalid annotation for interpolated context menu command.")

    async def invoke(self, ctx: SlashContext) -> None:
        if not isinstance(ctx, SlashContext):
            return
        return await super().invoke(ctx)

    def to_application_command(self) -> discord.ApplicationCommand:
        """Convert the current command instance to an application command.

        Returns
        -------
        :class:`discord.ApplicationCommand`
            An application command equivelant to the current command instance.
        """

        localizations = None
        default_member_permissions = None
        guild_only = False
        if self.application_command_meta is not None:
            localizations = self.application_command_meta.name_localizations
            default_member_permissions = self.application_command_meta.permissions
            guild_only = self.application_command_meta.guild_only
        command = discord.ApplicationCommand(
            name=self.name,
            type=self.application_command_type,
            name_localizations=localizations,
            default_member_permissions=default_member_permissions,
            dm_permissions=not guild_only,
        )
        return command


class GroupMixin(Generic[CogT]):
    """A mixin that implements common functionality for classes that behave
    similar to :class:`.Group` and are allowed to register commands.

    Attributes
    -----------
    all_commands: :class:`dict`
        A mapping of command name to :class:`.Command`
        objects.
    case_insensitive: :class:`bool`
        Whether the commands should be case insensitive. Defaults to ``False``.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        case_insensitive = kwargs.get('case_insensitive', False)
        self.all_commands: Dict[str, Command[CogT, Any, Any]] = _CaseInsensitiveDict() if case_insensitive else {}
        self.case_insensitive: bool = case_insensitive
        super().__init__(*args, **kwargs)

    @property
    def commands(self) -> Set[Command[CogT, Any, Any]]:
        """Set[:class:`.Command`]: A unique set of commands without aliases that are registered."""
        return set(self.all_commands.values())

    def recursively_remove_all_commands(self) -> None:
        for command in self.all_commands.copy().values():
            if isinstance(command, GroupMixin):
                command.recursively_remove_all_commands()
            self.remove_command(command.name)

    def add_command(self, command: Command[CogT, Any, Any]) -> None:
        """Adds a :class:`.Command` into the internal list of commands.

        This is usually not called, instead the :meth:`~.GroupMixin.command` or
        :meth:`~.GroupMixin.group` shortcut decorators are used instead.

        Parameters
        -----------
        command: :class:`Command`
            The command to add.

        Raises
        -------
        :exc:`.CommandRegistrationError`
            If the command or its alias is already registered by different command.
        TypeError
            If the command passed is not a subclass of :class:`.Command`.
        """

        if not isinstance(command, Command):
            raise TypeError('The command passed must be a subclass of Command')

        if isinstance(self, Command):
            command.parent = self

        if command.name in self.all_commands:
            raise CommandRegistrationError(command.name)

        self.all_commands[command.name] = command
        for alias in command.aliases:
            if alias in self.all_commands:
                self.remove_command(command.name)
                raise CommandRegistrationError(alias, alias_conflict=True)
            self.all_commands[alias] = command

    def remove_command(self, name: str) -> Optional[Command[CogT, Any, Any]]:
        """Remove a :class:`.Command` from the internal list
        of commands.

        This could also be used as a way to remove aliases.

        Parameters
        -----------
        name: :class:`str`
            The name of the command to remove.

        Returns
        --------
        Optional[:class:`.Command`]
            The command that was removed. If the name is not valid then
            ``None`` is returned instead.
        """
        command = self.all_commands.pop(name, None)

        # does not exist
        if command is None:
            return None

        if name in command.aliases:
            # we're removing an alias so we don't want to remove the rest
            return command

        # we're not removing the alias so let's delete the rest of them.
        for alias in command.aliases:
            cmd = self.all_commands.pop(alias, None)
            # in the case of a CommandRegistrationError, an alias might conflict
            # with an already existing command. If this is the case, we want to
            # make sure the pre-existing command is not removed.
            if cmd is not None and cmd != command:
                self.all_commands[alias] = cmd
        return command

    def walk_commands(self) -> Generator[Command[CogT, Any, Any], None, None]:
        """An iterator that recursively walks through all commands and subcommands.

        Yields
        ------
        Union[:class:`.Command`, :class:`.Group`]
            A command or group from the internal list of commands.
        """
        for command in self.commands:
            yield command
            if isinstance(command, GroupMixin):
                yield from command.walk_commands()

    def get_command(self, name: str, *, ignore_spaces: bool = False) -> Optional[Command[CogT, Any, Any]]:
        """Get a :class:`.Command` from the internal list
        of commands.

        This could also be used as a way to get aliases.

        The name could be fully qualified (e.g. ``'foo bar'``) will get
        the subcommand ``bar`` of the group command ``foo``. If a
        subcommand is not found then ``None`` is returned just as usual.

        Parameters
        -----------
        name: :class:`str`
            The name of the command to get.
        ignore_spaces: Optional[:class:`bool`]
            Whether to ignore spaces when looking for the command by its name.

            .. versionadded:: 0.0.4

        Returns
        --------
        Optional[:class:`Command`]
            The command that was requested. If not found, returns ``None``.
        """

        # fast path, no space in name.
        if ' ' not in name or ignore_spaces:
            return self.all_commands.get(name)

        names = name.split()
        if not names:
            return None
        obj = self.all_commands.get(names[0])
        if not isinstance(obj, GroupMixin):
            return obj

        for name in names[1:]:
            try:
                obj = obj.all_commands[name]  # type: ignore
            except (AttributeError, KeyError):
                return None

        return obj

    @overload
    def command(
        self,
        name: str = ...,
        cls: Type[Command[CogT, P, T]] = ...,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[
        [
            Union[
                Callable[Concatenate[CogT, ContextT, P], Coro[T]],
                Callable[Concatenate[ContextT, P], Coro[T]],
            ]
        ], Command[CogT, P, T]]:
        ...

    @overload
    def command(
        self,
        name: str = ...,
        cls: Type[CommandT] = ...,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[Concatenate[ContextT, P], Coro[Any]]], CommandT]:
        ...

    def command(
        self,
        name: str = MISSING,
        cls: Type[CommandT] = MISSING,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[Concatenate[ContextT, P], Coro[Any]]], CommandT]:
        """A shortcut decorator that invokes :func:`.command` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.

        Returns
        --------
        Callable[..., :class:`Command`]
            A decorator that converts the provided method into a Command, adds it to the bot, then returns it.
        """
        def decorator(func: Callable[Concatenate[ContextT, P], Coro[Any]]) -> CommandT:
            kwargs.setdefault('parent', self)
            result = command(name=name, cls=cls, *args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    @overload
    def group(
        self,
        name: str = ...,
        cls: Type[Group[CogT, P, T]] = ...,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[
            Union[
                Callable[Concatenate[CogT, ContextT, P], Coro[T]],
                Callable[Concatenate[ContextT, P], Coro[T]]
            ]
        ], Group[CogT, P, T]]:
        ...

    @overload
    def group(
        self,
        name: str = ...,
        cls: Type[GroupT] = ...,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[Concatenate[ContextT, P], Coro[Any]]], GroupT]:
        ...

    def group(
        self,
        name: str = MISSING,
        cls: Type[GroupT] = MISSING,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[Concatenate[ContextT, P], Coro[Any]]], GroupT]:
        """A shortcut decorator that invokes :func:`.group` and adds it to
        the internal command list via :meth:`~.GroupMixin.add_command`.

        Returns
        --------
        Callable[..., :class:`Group`]
            A decorator that converts the provided method into a Group, adds it to the bot, then returns it.
        """
        def decorator(func: Callable[Concatenate[ContextT, P], Coro[Any]]) -> GroupT:
            kwargs.setdefault('parent', self)
            result = group(name=name, cls=cls, *args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator


class Group(GroupMixin[CogT], Command[CogT, P, T]):
    """A class that implements a grouping protocol for commands to be
    executed as subcommands.

    This class is a subclass of :class:`.Command` and thus all options
    valid in :class:`.Command` are valid in here as well.

    Attributes
    -----------
    invoke_without_command: :class:`bool`
        Indicates if the group callback should begin parsing and
        invocation only if no subcommand was found. Useful for
        making it an error handling function to tell the user that
        no subcommand was found or to have different functionality
        in case no subcommand was found. If this is ``False``, then
        the group callback will always be invoked first. This means
        that the checks and the parsing dictated by its parameters
        will be executed. Defaults to ``False``.
    case_insensitive: :class:`bool`
        Indicates if the group's commands should be case insensitive.
        Defaults to ``False``.
    """
    def __init__(self, *args: Any, **attrs: Any) -> None:
        self.invoke_without_command: bool = attrs.pop('invoke_without_command', False)
        super().__init__(*args, **attrs)

    def copy(self: GroupT) -> GroupT:
        """Creates a copy of this :class:`Group`.

        Returns
        --------
        :class:`Group`
            A new instance of this group.
        """
        ret = super().copy()
        for cmd in self.commands:
            ret.add_command(cmd.copy())
        return ret  # type: ignore

    async def invoke(self, ctx: Context) -> None:
        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        early_invoke = not self.invoke_without_command
        if early_invoke:
            await self.prepare(ctx)

        view = ctx.view
        previous = view.index
        view.skip_ws()
        trigger = view.get_word()

        if trigger:
            ctx.subcommand_passed = trigger
            ctx.invoked_subcommand = self.all_commands.get(trigger, None)

        if early_invoke:
            injected = hooked_wrapped_callback(self, ctx, self.callback)
            await injected(*ctx.args, **ctx.kwargs)

        ctx.invoked_parents.append(ctx.invoked_with)  # type: ignore

        if trigger and ctx.invoked_subcommand:
            ctx.invoked_with = trigger
            await ctx.invoked_subcommand.invoke(ctx)
        elif not early_invoke:
            # undo the trigger parsing
            view.index = previous
            view.previous = previous
            await super().invoke(ctx)

    async def reinvoke(self, ctx: Context, *, call_hooks: bool = False) -> None:
        ctx.invoked_subcommand = None
        early_invoke = not self.invoke_without_command
        if early_invoke:
            ctx.command = self
            await self._parse_arguments(ctx)

            if call_hooks:
                await self.call_before_hooks(ctx)

        view = ctx.view
        previous = view.index
        view.skip_ws()
        trigger = view.get_word()

        if trigger:
            ctx.subcommand_passed = trigger
            ctx.invoked_subcommand = self.all_commands.get(trigger, None)

        if early_invoke:
            try:
                await self.callback(*ctx.args, **ctx.kwargs)  # type: ignore
            except:
                ctx.command_failed = True
                raise
            finally:
                if call_hooks:
                    await self.call_after_hooks(ctx)

        ctx.invoked_parents.append(ctx.invoked_with)  # type: ignore

        if trigger and ctx.invoked_subcommand:
            ctx.invoked_with = trigger
            await ctx.invoked_subcommand.reinvoke(ctx, call_hooks=call_hooks)
        elif not early_invoke:
            # undo the trigger parsing
            view.index = previous
            view.previous = previous
            await super().reinvoke(ctx, call_hooks=call_hooks)

    def to_application_command(self) -> Union[discord.ApplicationCommand, discord.ApplicationCommandOption]:
        """Convert the current command instance to an application command.

        Returns
        --------
        :class:`discord.ApplicationCommand`
            An application command equivelant to the current command instance.
        """

        localizations = None
        default_member_permissions = None
        guild_only = False
        if self.application_command_meta is not None:
            localizations = self.application_command_meta.name_localizations
            default_member_permissions = self.application_command_meta.permissions
            guild_only = self.application_command_meta.guild_only
        if self.parent is None:  # No parent, this is the base
            command = discord.ApplicationCommand(
                name=self.name,
                description=self.short_doc or self.name,
                name_localizations=localizations,
                default_member_permissions=default_member_permissions,
                dm_permissions=not guild_only,
            )
        else:  # Parent is another group
            command = discord.ApplicationCommandOption(
                name=self.name,
                type=discord.ApplicationCommandOptionType.subcommand_group,
                description=self.short_doc or self.name,
                name_localizations=localizations,
            )
        for c in self.commands:
            if not c.application_command_meta:
                continue
            a = c.to_application_command()
            assert isinstance(a, discord.ApplicationCommandOption)
            command.add_option(a)
        return command


# Decorators

@overload
def command(
    name: str = ...,
    cls: Type[Command[CogT, P, T]] = ...,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ]
    ]
, Command[CogT, P, T]]:
    ...


@overload
def command(
    name: str = ...,
    cls: Type[CommandT] = ...,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],
            Callable[Concatenate[ContextT, P], Coro[Any]],
        ]
    ]
, CommandT]:
    ...


def command(
    name: str = MISSING,
    cls: Type[CommandT] = MISSING,
    **attrs: Any
) -> Callable[
    [
        Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
        ]
    ]
, Union[Command[CogT, P, T], CommandT]]:
    """A decorator that transforms a function into a :class:`.Command`
    or if called with :func:`.group`, :class:`.Group`.

    By default the ``help`` attribute is received automatically from the
    docstring of the function and is cleaned up with the use of
    ``inspect.cleandoc``. If the docstring is ``bytes``, then it is decoded
    into :class:`str` using utf-8 encoding.

    All checks added using the :func:`.check` & co. decorators are added into
    the function. There is no way to supply your own checks through this
    decorator.

    Parameters
    -----------
    name: :class:`str`
        The name to create the command with. By default this uses the
        function name unchanged.
    cls
        The class to construct with. By default this is :class:`.Command`.
        You usually do not change this.
    attrs
        Keyword arguments to pass into the construction of the class denoted
        by ``cls``.

    Raises
    -------
    TypeError
        If the function is not a coroutine or is already a command.
    """
    if cls is MISSING:
        cls = Command  # type: ignore

    def decorator(func: Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],
        ]) -> CommandT:
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)

    return decorator


@overload
def context_command(
    name: str = ...,
    cls: Type[Command[CogT, P, T]] = ...,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ]
    ]
, Command[CogT, P, T]]:
    ...


@overload
def context_command(
    name: str = ...,
    cls: Type[CommandT] = ...,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],
            Callable[Concatenate[ContextT, P], Coro[Any]],
        ]
    ]
, CommandT]:
    ...


def context_command(
    name: str = MISSING,
    cls: Type[CommandT] = MISSING,
    **attrs: Any
) -> Callable[
    [
        Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
        ]
    ]
, Union[Command[CogT, P, T], CommandT]]:
    """A decorator that transforms a function into a :class:`.ContextMenuCommand`.

    By default the ``help`` attribute is received automatically from the
    docstring of the function and is cleaned up with the use of
    ``inspect.cleandoc``. If the docstring is ``bytes``, then it is decoded
    into :class:`str` using utf-8 encoding.

    All checks added using the :func:`.check` & co. decorators are added into
    the function. There is no way to supply your own checks through this
    decorator.

    The application type of the context command is determined automatically by the
    type hinting on its parameters.

    .. versionadded:: 0.0.3

    Parameters
    -----------
    name: :class:`str`
        The name to create the command with. By default this uses the
        function name unchanged.
    cls
        The class to construct with. By default this is :class:`.ContextMenuCommand`.
        You usually do not change this.
    attrs
        Keyword arguments to pass into the construction of the class denoted
        by ``cls``.

    Raises
    -------
    TypeError
        If the function is not a coroutine or is already a command.
    """
    if cls is MISSING:
        cls = ContextMenuCommand  # type: ignore

    def decorator(func: Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],
        ]) -> CommandT:
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, type=type, **attrs)

    return decorator


@overload
def group(
    name: str = ...,
    cls: Type[Group[CogT, P, T]] = ...,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
            Callable[Concatenate[ContextT, P], Coro[T]],
        ]
    ]
, Group[CogT, P, T]]:
    ...


@overload
def group(
    name: str = ...,
    cls: Type[GroupT] = ...,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[CogT, ContextT, P], Coro[Any]],
            Callable[Concatenate[ContextT, P], Coro[Any]],
        ]
    ]
, GroupT]:
    ...


def group(
    name: str = MISSING,
    cls: Type[GroupT] = MISSING,
    **attrs: Any,
) -> Callable[
    [
        Union[
            Callable[Concatenate[ContextT, P], Coro[Any]],
            Callable[Concatenate[CogT, ContextT, P], Coro[T]],
        ]
    ]
, Union[Group[CogT, P, T], GroupT]]:
    """A decorator that transforms a function into a :class:`.Group`.

    This is similar to the :func:`.command` decorator but the ``cls``
    parameter is set to :class:`Group` by default.
    """
    if cls is MISSING:
        cls = Group  # type: ignore
    return command(name=name, cls=cls, **attrs)  # type: ignore


def check(predicate: Check) -> Callable[[T], T]:
    r"""A decorator that adds a check to the :class:`.Command` or its
    subclasses. These checks could be accessed via :attr:`.Command.checks`.

    These checks should be predicates that take in a single parameter taking
    a :class:`.Context`. If the check returns a ``False``\-like value then
    during invocation a :exc:`.CheckFailure` exception is raised and sent to
    the :func:`.on_command_error` event.

    If an exception should be thrown in the predicate then it should be a
    subclass of :exc:`.CommandError`. Any exception not subclassed from it
    will be propagated while those subclassed will be sent to
    :func:`.on_command_error`.

    A special attribute named ``predicate`` is bound to the value
    returned by this decorator to retrieve the predicate passed to the
    decorator. This allows the following introspection and chaining to be done:

    .. code-block:: python3

        def owner_or_permissions(**perms):
            original = commands.has_permissions(**perms).predicate
            async def extended_check(ctx):
                if ctx.guild is None:
                    return False
                return ctx.guild.owner_id == ctx.author.id or await original(ctx)
            return commands.check(extended_check)

    .. note::

        The function returned by ``predicate`` is **always** a coroutine,
        even if the original function was not a coroutine.

    Examples
    ---------

    Creating a basic check to see if the command invoker is you.

    .. code-block:: python3

        def check_if_it_is_me(ctx):
            return ctx.message.author.id == 85309593344815104

        @bot.command()
        @commands.check(check_if_it_is_me)
        async def only_for_me(ctx):
            await ctx.send('I know you!')

    Transforming common checks into its own decorator:

    .. code-block:: python3

        def is_me():
            def predicate(ctx):
                return ctx.message.author.id == 85309593344815104
            return commands.check(predicate)

        @bot.command()
        @is_me()
        async def only_me(ctx):
            await ctx.send('Only you!')

    Parameters
    -----------
    predicate: Callable[[:class:`Context`], :class:`bool`]
        The predicate to check if the command should be invoked.
    """

    def decorator(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(func, Command):
            func.checks.append(predicate)
        else:
            if not hasattr(func, '__commands_checks__'):
                func.__commands_checks__ = []

            func.__commands_checks__.append(predicate)

        return func

    if inspect.iscoroutinefunction(predicate):
        decorator.predicate = predicate
    else:
        @functools.wraps(predicate)
        async def wrapper(ctx):
            return predicate(ctx)  # type: ignore
        decorator.predicate = wrapper

    return decorator  # type: ignore


def check_any(*checks: Check) -> Callable[[T], T]:
    r"""A :func:`check` that is added that checks if any of the checks passed
    will pass, i.e. using logical OR.

    If all checks fail then :exc:`.CheckAnyFailure` is raised to signal the failure.
    It inherits from :exc:`.CheckFailure`.

    .. note::

        The ``predicate`` attribute for this function **is** a coroutine.

    Parameters
    ------------
    \*checks: Callable[[:class:`Context`], :class:`bool`]
        An argument list of checks that have been decorated with
        the :func:`check` decorator.

    Raises
    -------
    TypeError
        A check passed has not been decorated with the :func:`check`
        decorator.

    Examples
    ---------

    Creating a basic check to see if it's the bot owner or
    the server owner:

    .. code-block:: python3

        def is_guild_owner():
            def predicate(ctx):
                return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
            return commands.check(predicate)

        @bot.command()
        @commands.check_any(commands.is_owner(), is_guild_owner())
        async def only_for_owners(ctx):
            await ctx.send('Hello mister owner!')
    """

    unwrapped = []
    for wrapped in checks:
        try:
            pred = wrapped.predicate
        except AttributeError:
            raise TypeError(f'{wrapped!r} must be wrapped by commands.check decorator') from None
        else:
            unwrapped.append(pred)

    async def predicate(ctx: Context) -> bool:
        errors = []
        for func in unwrapped:
            try:
                value = await func(ctx)
            except CheckFailure as e:
                errors.append(e)
            else:
                if value:
                    return True
        # if we're here, all checks failed
        raise CheckAnyFailure(unwrapped, errors)

    return check(predicate)


def has_role(item: Union[int, str]) -> Callable[[T], T]:
    """A :func:`.check` that is added that checks if the member invoking the
    command has the role specified via the name or ID specified.

    If a string is specified, you must give the exact name of the role, including
    caps and spelling.

    If an integer is specified, you must give the exact snowflake ID of the role.

    If the message is invoked in a private message context then the check will
    return ``False``.

    This check raises one of two special exceptions, :exc:`.MissingRole` if the user
    is missing a role, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.

    Parameters
    -----------
    item: Union[:class:`int`, :class:`str`]
        The name or ID of the role to check.
    """

    def predicate(ctx: Context) -> bool:
        if ctx.guild is None:
            raise NoPrivateMessage()

        # ctx.guild is None doesn't narrow ctx.author to Member
        if isinstance(item, int):
            role = discord.utils.get(ctx.author.roles, id=item)  # type: ignore
        else:
            role = discord.utils.get(ctx.author.roles, name=item)  # type: ignore
        if role is None:
            raise MissingRole(item)
        return True

    return check(predicate)


def has_any_role(*items: Union[int, str]) -> Callable[[T], T]:
    r"""A :func:`.check` that is added that checks if the member invoking the
    command has **any** of the roles specified. This means that if they have
    one out of the three roles specified, then this check will return `True`.

    Similar to :func:`.has_role`\, the names or IDs passed in must be exact.

    This check raises one of two special exceptions, :exc:`.MissingAnyRole` if the user
    is missing all roles, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.

    Parameters
    -----------
    items: List[Union[:class:`str`, :class:`int`]]
        An argument list of names or IDs to check that the member has roles wise.

    Example
    --------

    .. code-block:: python3

        @bot.command()
        @commands.has_any_role('Library Devs', 'Moderators', 492212595072434186)
        async def cool(ctx):
            await ctx.send('You are cool indeed')
    """
    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        # ctx.guild is None doesn't narrow ctx.author to Member
        getter = functools.partial(discord.utils.get, ctx.author.roles)  # type: ignore
        if any(getter(id=item) is not None if isinstance(item, int) else getter(name=item) is not None for item in items):
            return True
        raise MissingAnyRole(list(items))

    return check(predicate)


def bot_has_role(item: int) -> Callable[[T], T]:
    """Similar to :func:`.has_role` except checks if the bot itself has the
    role.

    This check raises one of two special exceptions, :exc:`.BotMissingRole` if the bot
    is missing the role, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.
    """

    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        me = ctx.me
        if isinstance(item, int):
            role = discord.utils.get(me.roles, id=item)
        else:
            role = discord.utils.get(me.roles, name=item)
        if role is None:
            raise BotMissingRole(item)
        return True
    return check(predicate)


def bot_has_any_role(*items: int) -> Callable[[T], T]:
    """Similar to :func:`.has_any_role` except checks if the bot itself has
    any of the roles listed.

    This check raises one of two special exceptions, :exc:`.BotMissingAnyRole` if the bot
    is missing all roles, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.
    """
    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        me = ctx.me
        getter = functools.partial(discord.utils.get, me.roles)
        if any(getter(id=item) is not None if isinstance(item, int) else getter(name=item) is not None for item in items):
            return True
        raise BotMissingAnyRole(list(items))
    return check(predicate)


def has_permissions(**perms: bool) -> Callable[[T], T]:
    """A :func:`.check` that is added that checks if the member has all of
    the permissions necessary.

    Note that this check operates on the current channel permissions, not the
    guild wide permissions.

    The permissions passed in must be exactly like the properties shown under
    :class:`.discord.Permissions`.

    This check raises a special exception, :exc:`.MissingPermissions`
    that is inherited from :exc:`.CheckFailure`.

    Parameters
    ------------
    perms
        An argument list of permissions to check for.

    Example
    ---------

    .. code-block:: python3

        @bot.command()
        @commands.has_permissions(manage_messages=True)
        async def test(ctx):
            await ctx.send('You can manage messages.')

    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: Context) -> bool:
        ch = ctx.channel

        if hasattr(ctx, "interaction"):
            permissions = ctx.interaction.permissions  # type: ignore
        else:
            permissions = ch.permissions_for(ctx.author)  # type: ignore

        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if not missing:
            return True

        raise MissingPermissions(missing)

    return check(predicate)


def bot_has_permissions(**perms: bool) -> Callable[[T], T]:
    """Similar to :func:`.has_permissions` except checks if the bot itself has
    the permissions listed.

    This check raises a special exception, :exc:`.BotMissingPermissions`
    that is inherited from :exc:`.CheckFailure`.
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: Context) -> bool:
        guild = ctx.guild
        me = getattr(guild, "me", None) if guild is not None else ctx.bot.user

        newperms = perms.copy()
        if isinstance(ctx, SlashContext):
            for p in SLASH_PERMISSION_IGNORES:
                v = newperms.pop(p, None)
                if v is False:
                    newperms[p] = v
            permissions = ctx.interaction.app_permissions
        else:
            permissions = ctx.channel.permissions_for(me)  # type: ignore - messageable channel union
        if not newperms:
            return True

        missing = [
            perm
            for perm, value in newperms.items()
            if getattr(permissions, perm) != value
        ]

        if not missing:
            return True

        raise BotMissingPermissions(missing)

    return check(predicate)


def has_guild_permissions(**perms: bool) -> Callable[[T], T]:
    """Similar to :func:`.has_permissions`, but operates on guild wide
    permissions instead of the current channel permissions.

    If this check is called in a DM context, it will raise an
    exception, :exc:`.NoPrivateMessage`.
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: Context) -> bool:
        if not ctx.guild:
            raise NoPrivateMessage

        permissions = ctx.author.guild_permissions  # type: ignore
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if not missing:
            return True

        raise MissingPermissions(missing)

    return check(predicate)


def bot_has_guild_permissions(**perms: bool) -> Callable[[T], T]:
    """Similar to :func:`.has_guild_permissions`, but checks the bot
    members guild permissions.
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: Context) -> bool:
        if not ctx.guild:
            raise NoPrivateMessage

        permissions = ctx.me.guild_permissions  # type: ignore
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if isinstance(ctx, SlashContext):
            missing = [i for i in missing if i not in SLASH_PERMISSION_IGNORES]

        if not missing:
            return True

        raise BotMissingPermissions(missing)

    return check(predicate)


def dm_only() -> Callable[[T], T]:
    """A :func:`.check` that indicates this command must only be used in a
    DM context. Only private messages are allowed when
    using the command.

    This check raises a special exception, :exc:`.PrivateMessageOnly`
    that is inherited from :exc:`.CheckFailure`.
    """

    def predicate(ctx: Context) -> bool:
        if isinstance(ctx, SlashContext):
            check = ctx.interaction.guild_id is None
        else:
            check = ctx.guild is None
        if not check:
            raise PrivateMessageOnly()
        return True

    return check(predicate)


def guild_only() -> Callable[[T], T]:
    """A :func:`.check` that indicates this command must only be used in a
    guild context only. Basically, no private messages are allowed when
    using the command.

    This check raises a special exception, :exc:`.NoPrivateMessage`
    that is inherited from :exc:`.CheckFailure`.
    """

    def predicate(ctx: Context) -> bool:
        if isinstance(ctx, SlashContext):
            check = ctx.interaction.guild_id is None
        else:
            check = ctx.guild is None
        if check:
            raise NoPrivateMessage()
        return True

    return check(predicate)


def is_owner() -> Callable[[T], T]:
    """A :func:`.check` that checks if the person invoking this command is the
    owner of the bot.

    This is powered by :meth:`.Bot.is_owner`.

    This check raises a special exception, :exc:`.NotOwner` that is derived
    from :exc:`.CheckFailure`.
    """

    async def predicate(ctx: Context) -> bool:
        if not await ctx.bot.is_owner(ctx.author):
            raise NotOwner('You do not own this bot.')
        return True

    return check(predicate)


def is_nsfw() -> Callable[[T], T]:
    """A :func:`.check` that checks if the channel is a NSFW channel.

    This check raises a special exception, :exc:`.NSFWChannelRequired`
    that is derived from :exc:`.CheckFailure`.
    """
    def pred(ctx: Context) -> bool:
        ch = ctx.channel
        if ctx.guild is None or (isinstance(ch, (discord.TextChannel, discord.Thread)) and ch.is_nsfw()):
            return True
        raise NSFWChannelRequired(ch)  # type: ignore
    return check(pred)


def cooldown(rate: int, per: float, type: Union[BucketType, Callable[[Message], Any]] = BucketType.default) -> Callable[[T], T]:
    """A decorator that adds a cooldown to a :class:`.Command`

    A cooldown allows a command to only be used a specific amount
    of times in a specific time frame. These cooldowns can be based
    either on a per-guild, per-channel, per-user, per-role or global basis.
    Denoted by the third argument of ``type`` which must be of enum
    type :class:`.BucketType`.

    If a cooldown is triggered, then :exc:`.CommandOnCooldown` is triggered in
    :func:`.on_command_error` and the local error handler.

    A command can only have a single cooldown.

    Parameters
    ------------
    rate: :class:`int`
        The number of times a command can be used before triggering a cooldown.
    per: :class:`float`
        The amount of seconds to wait for a cooldown when it's been triggered.
    type: Union[:class:`.BucketType`, Callable[[:class:`.Message`], Any]]
        The type of cooldown to have. If callable, should return a key for the mapping.
    """

    def decorator(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(func, Command):
            func._buckets = CooldownMapping(Cooldown(rate, per), type)
        else:
            func.__commands_cooldown__ = CooldownMapping(Cooldown(rate, per), type)
        return func
    return decorator  # type: ignore


def dynamic_cooldown(cooldown: Union[BucketType, Callable[[Message], Any]], type: BucketType = BucketType.default) -> Callable[[T], T]:
    """A decorator that adds a dynamic cooldown to a :class:`.Command`

    This differs from :func:`.cooldown` in that it takes a function that
    accepts a single parameter of type :class:`.discord.Message` and must
    return a :class:`.Cooldown` or ``None``. If ``None`` is returned then
    that cooldown is effectively bypassed.

    A cooldown allows a command to only be used a specific amount
    of times in a specific time frame. These cooldowns can be based
    either on a per-guild, per-channel, per-user, per-role or global basis.
    Denoted by the third argument of ``type`` which must be of enum
    type :class:`.BucketType`.

    If a cooldown is triggered, then :exc:`.CommandOnCooldown` is triggered in
    :func:`.on_command_error` and the local error handler.

    A command can only have a single cooldown.

    Parameters
    ------------
    cooldown: Callable[[:class:`.discord.Message`], Optional[:class:`.Cooldown`]]
        A function that takes a message and returns a cooldown that will
        apply to this invocation or ``None`` if the cooldown should be bypassed.
    type: :class:`.BucketType`
        The type of cooldown to have.
    """
    if not callable(cooldown):
        raise TypeError("A callable must be provided")

    def decorator(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(func, Command):
            func._buckets = DynamicCooldownMapping(cooldown, type)
        else:
            func.__commands_cooldown__ = DynamicCooldownMapping(cooldown, type)
        return func
    return decorator  # type: ignore


def max_concurrency(number: int, per: BucketType = BucketType.default, *, wait: bool = False) -> Callable[[T], T]:
    """A decorator that adds a maximum concurrency to a :class:`.Command` or its subclasses.

    This enables you to only allow a certain number of command invocations at the same time,
    for example if a command takes too long or if only one user can use it at a time. This
    differs from a cooldown in that there is no set waiting period or token bucket -- only
    a set number of people can run the command.

    Parameters
    -------------
    number: :class:`int`
        The maximum number of invocations of this command that can be running at the same time.
    per: :class:`.BucketType`
        The bucket that this concurrency is based on, e.g. ``BucketType.guild`` would allow
        it to be used up to ``number`` times per guild.
    wait: :class:`bool`
        Whether the command should wait for the queue to be over. If this is set to ``False``
        then instead of waiting until the command can run again, the command raises
        :exc:`.MaxConcurrencyReached` to its error handler. If this is set to ``True``
        then the command waits until it can be executed.
    """

    def decorator(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        value = MaxConcurrency(number, per=per, wait=wait)
        if isinstance(func, Command):
            func._max_concurrency = value
        else:
            func.__commands_max_concurrency__ = value
        return func
    return decorator  # type: ignore


def before_invoke(coro) -> Callable[[T], T]:
    """A decorator that registers a coroutine as a pre-invoke hook.

    This allows you to refer to one before invoke hook for several commands that
    do not have to be within the same cog.

    Example
    ---------

    .. code-block:: python3

        async def record_usage(ctx):
            print(ctx.author, 'used', ctx.command, 'at', ctx.message.created_at)

        @bot.command()
        @commands.before_invoke(record_usage)
        async def who(ctx): # Output: <User> used who at <Time>
            await ctx.send('i am a bot')

        class What(commands.Cog):

            @commands.before_invoke(record_usage)
            @commands.command()
            async def when(self, ctx): # Output: <User> used when at <Time>
                await ctx.send(f'and i have existed since {ctx.bot.user.created_at}')

            @commands.command()
            async def where(self, ctx): # Output: <Nothing>
                await ctx.send('on Discord')

            @commands.command()
            async def why(self, ctx): # Output: <Nothing>
                await ctx.send('because someone made me')

        bot.add_cog(What())
    """
    def decorator(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(func, Command):
            func.before_invoke(coro)
        else:
            func.__before_invoke__ = coro
        return func
    return decorator  # type: ignore


def after_invoke(coro) -> Callable[[T], T]:
    """A decorator that registers a coroutine as a post-invoke hook.

    This allows you to refer to one after invoke hook for several commands that
    do not have to be within the same cog.
    """
    def decorator(func: Union[Command, CoroFunc]) -> Union[Command, CoroFunc]:
        if isinstance(func, Command):
            func.after_invoke(coro)
        else:
            func.__after_invoke__ = coro
        return func
    return decorator  # type: ignore


def defer(*, ephemeral: bool = False):
    """A decorator that has your context send a defer response before continuing with the command.

    Parameters
    -----------
    ephemeral: Optional[:class:`bool`]
        Whether or not the defer should be ephemeral.
    """

    async def predicate(ctx):
        await ctx.defer(ephemeral=ephemeral)
        return True
    return check(predicate)


def is_slash_command(*, check_scopes: bool = False):
    """
    The check for whether or not the command was invoved from an application command
    (as defined by `ctx` being an instance of :class:`discord.ext.commands.SlashContext`).

    .. versionadded:: 0.0.4

    Parameters
    ---------------
    check_scopes: Optional[:class:`bool`]
        Whether or not to check the bot has the ``applications.commands`` scope in the guild.

        .. versionadded:: 0.0.8

    Raises
    ------------
    :class:`IsNotSlashCommand`
        If the command isn't being used in a slash command.
    """

    async def predicate(ctx: Union[Context, SlashContext]):

        # It's a slashie
        if isinstance(ctx, SlashContext):
            return True

        # It's not a slashie but we don't care about scopes or it's a DM
        if not check_scopes or ctx.guild is None:
            raise IsNotSlashCommand()

        # Let's see if we have scopes
        try:
            await ctx.guild.fetch_application_commands()
        except discord.Forbidden:
            raise IsNotSlashCommand(missing_scope=True)
        raise IsNotSlashCommand(missing_scope=False)

    return check(predicate)
