"""
Logic of the all user commands.
"""

import logging.handlers
from typing import Any, Union

import discord
import psycopg
from discord.ext import commands

from .attrs import TargetGroupAttrs
from .converters import (
	SearchExpression,
	ShortSearchExpression,
	SpecialExpression
)
from .data import ActGroup, TargetGroup
from .embeds import ErrorEmbed, SuccessEmbed
from .exceptions import UnhandlePartMessageSignal, UnsupportedLanguage
from .flags import UserLogFlags
from .main import BotConstructor
from .utils import ContextProvider, Language, Translator, removeNesting

logger = logging.getLogger(__name__)

class Settings(commands.Cog):

	def __init__(
		self,
		bot: commands.Bot,
		dbconn: psycopg.AsyncConnection[Any],
		i18n: Translator
	) -> None:
		self.bot = bot
		self.dbconn: psycopg.AsyncConnection[Any] = dbconn
		self.translator = i18n

	async def cog_command_error(
		self,
		ctx: commands.Context,
		error: Exception
	) -> None:
		embed_to_send: ErrorEmbed
		if isinstance(error.original.__class__, UnsupportedLanguage.__class__):
			embed_to_send = ErrorEmbed().add_field(
				name=self.translator("error"),
				value=self.translator(error.original))
		await ctx.send(embed=embed_to_send) if embed_to_send else None

	@commands.group(invoke_without_command=True)
	async def setup(
		self,
		ctx: commands.Context
	):
		"""
		The command to manage bot settings.
		"""
		if ctx.guild:
			await self.translator.installBindedLanguage(ctx.guild.id)
		elif ctx.author.id:
			raise NotImplementedError
		embed = ErrorEmbed().add_field(name=self.translator("error"),
		value=self.translator("make_sure_subcommand"))
		await ctx.send(embed=embed)

	@setup.command(aliases=["lang"])
	async def language(
		self,
		ctx: commands.Context,
		lang_name: str,
	) -> None:
		"""
		It sets a language the bot will use to communicate.

		:param lang_name: Short or full language name ("en"/"english").
		Currently only available is english and russian (command docs are
		temporarily not translated).
		"""
		lang_instance: Language
		if len(lang_name) == 2:
			lang_instance = Language(short_name=lang_name)
		else:
			lang_instance = Language(full_name=lang_name)
		if ctx.guild:
			await self.translator.bindLanguage(lang_instance, ctx.guild.id)
			await self.translator.installBindedLanguage(ctx.guild.id)
		elif ctx.author.id:
			raise NotImplementedError
		embed_to_send = SuccessEmbed().add_field(
			name=self.translator("success"),
			value=self.translator("success_bot_language_set")
		)
		await ctx.send(embed=embed_to_send)

class UserLog(commands.Cog):

	def __init__(
		self,
		bot: commands.Bot,
		dbconn: psycopg.AsyncConnection[Any],
		context_provider: ContextProvider,
	) -> None:
		self.bot = bot
		self.dbconn: psycopg.AsyncConnection[Any] = dbconn
		self.context_provider: ContextProvider = context_provider

	async def cog_command_error(
		self,
		ctx: commands.Context,
		error: Exception
	) -> None:
		"""
		The function for handling discord.py and custom errors.

		Raises:
			error: if the current error cannot be handled.
		"""
		if isinstance(error, commands.BadUnionArgument):
			await ctx.send("Убедитесь, что вы указали существующие "
				"объекты (\"{}\") в параметре {}, и у меня есть к ним доступ.".format(
				error.errors[0].argument, error.param.name)) # type: ignore
		elif isinstance(error, commands.MissingRequiredArgument):
			current_parameter = error.param.name
			await ctx.send(f"Убедитесь, что вы указали все обязательные "
				"параметры. Не найденный параметр:"
				f" {current_parameter}")
		elif isinstance(error.original, UnhandlePartMessageSignal): # type: ignore
			# this error is only passed as .original attr.
			await ctx.send("Убедитесь, что вы указали флаги явно, либо "
				"указали корректные данные."
				f" Необработанная часть сообщения: {ctx.current_argument}")
		else:
			logger.error(f"Unhadle exception {error}")
			raise error

	@commands.group(aliases=["logs"], invoke_without_command=True)
	async def log(self, ctx: commands.Context) -> None:
		"""
		The command provides subcommands for managing logs.
		"""
		await ctx.send("Убедитесь, что вы указали подкоманду.")

	@log.command(aliases=["1", "cr"]) # type: ignore[arg-type]
	async def create(
		self,
		ctx: commands.Context,
		target: commands.Greedy[Union[discord.TextChannel,
			discord.Member, discord.CategoryChannel, SearchExpression]],
		act: Union[ShortSearchExpression[ActGroup], str],
		d_in: commands.Greedy[Union[discord.TextChannel,
			discord.Member, SearchExpression, SpecialExpression]],
		*,
		flags: UserLogFlags
	) -> None:
		"""
		The subcommand for creating a logging rule.

		The arguments:
			target (@user, SearchExpression): who/what to watch.
			act (ShortSearchExpression, a name/ID of the action):
			what actions to watch. The greedy parameter.
			d_in (#channel/@user, SearchExpression, df/default):
			the receiver for logs. If "df" — in the default object. The
			greedy parameter.
		"""
		if not ctx.guild:
			return None

		self.context_provider.updateContext(ctx.guild)

		removeNesting(target)
		removeNesting(d_in)

		if not d_in: # if the last required parameter is omitted — the
			# exceptation isn't raised, so we have to work around it.
			raise commands.MissingRequiredArgument(ctx.
				command.clean_params["d_in"]) # type: ignore [union-attr]

		target_instance = TargetGroup(TargetGroupAttrs(
			self.dbconn,
			ctx.guild.id,
			target=target,  # type: ignore [arg-type]
			act=act,  # type: ignore [arg-type]
			d_in=d_in  # type: ignore [arg-type]
		)
		)

		for key in flags.get_flags().keys():
			if flags.__dict__[key]:
				setattr(target_instance, key, flags.__dict__[key])

		coincidence_targets_instance = await target_instance.extractData(
			target=target_instance.target,
			act=target_instance.act,
			d_in=target_instance.d_in,
			name=target_instance.name
		)
		if coincidence_targets_instance:
			coincidence_target = coincidence_targets_instance[0]
			await ctx.send(f"Цель с подобными параметрами уже существует: "
			f"{coincidence_target.dbrecord_id} ({coincidence_target.name})"
			f". Совпадающие элементы: "
			f"{target_instance.getCoincidenceTo(coincidence_target)}")
		else:
			await target_instance.writeData()
			await ctx.send("Цель добавлена успешно.")

async def setup(
	bot: BotConstructor, # type: ignore [name-defined]
) -> None:
	await bot.add_cog(UserLog(bot, bot.dbconn, bot.context_provider))
	await bot.add_cog(Settings(bot, bot.dbconn, bot.i18n_translator))