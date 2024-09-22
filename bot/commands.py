"""
Logic of the all user commands.
"""
import asyncio
import logging.handlers
from typing import Any, Union, List

import discord
import psycopg
from discord.ext import commands

from ._types import AND, OR
from .converters import (
	SearchExpression,
	ShortSearchExpression,
	SpecialExpression
)
from .data import (
	ActGroup,
	LogTarget,
	LogTargetFactory,
	createDBRecord,
	findFromDB
)
from .embeds import ErrorEmbed, SuccessEmbed
from .exceptions import (
	UnhandlePartMessageSignal,
	UnsupportedLanguage,
	UserException
)
from .flags import UserLogFlags, CreatingConvoyFlags
from .main import BotConstructor
from .utils import (ContextProvider, Language, Translator, removeNesting,
					RelativeDiscordTimestamp)
import datetime

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
		error: commands.CommandInvokeError # type: ignore[override]
	) -> None:
		embed_to_send: ErrorEmbed
		if (isinstance(error.original.__class__,
		UnsupportedLanguage.__class__) and # type: ignore[arg-type]
		isinstance(error.original, UserException)):
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

	@setup.command(aliases=["lang"]) # type: ignore[arg-type]
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
		act: Union[ShortSearchExpression[ActGroup], int],
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
				command.clean_params["d_in"]) # type: ignore[union-attr]

		flags_as_dict = dict(flags)

		log_target = LogTargetFactory(
			target=target, # type: ignore[arg-type]
			act=act, # type: ignore[arg-type]
			d_in=d_in, # type: ignore[arg-type]
			guild_id=ctx.guild.id,
			**flags_as_dict
		).getInstance()

		coincidence_log_targets = await findFromDB(
			dbconn=self.dbconn,
			db_object_class=LogTarget,
			guild_id=ctx.guild.id,
			target=target,
			act=str(act),
			d_in=d_in,
			name=flags_as_dict["name"],
			operators_dict_map={"0": AND, "1-4": OR}
		)

		if (coincidence_log_targets and
		isinstance(coincidence_target := coincidence_log_targets[0],
		LogTarget)):
			await ctx.send(f"Цель с подобными параметрами уже существует: "
			f"({coincidence_target.name}). "  # type: ignore[attr-defined]
			f"Совпадающие элементы: "
			f"{log_target.getCoincidenceTo(coincidence_target)}")
		else:
			await createDBRecord(self.dbconn, log_target)
			await ctx.send("Цель добавлена успешно.")

class ConvoyManager(commands.Cog):

	def __init__(
			self,
			bot: commands.Bot,
			dbconn: psycopg.AsyncConnection[Any],
			i18n: Translator,
	) -> None:
		self.bot = bot
		self.dbconn: psycopg.AsyncConnection[Any] = dbconn
		self.translator: Translator = i18n

	@commands.group(invoke_without_command=True)
	async def convoy(
		self,
		ctx: commands.Context
	):
		"""
		The command to manage convoys.
		"""
		if ctx.guild:
			await self.translator.installBindedLanguage(ctx.guild.id)
		elif ctx.author.id:
			raise NotImplementedError
		embed = ErrorEmbed().add_field(name=self.translator("error"),
		value=self.translator("make_sure_subcommand"))
		await ctx.send(embed=embed)

	@convoy.command(aliases=["cr"])  # type: ignore[arg-type]
	async def create(
			self,
			ctx: commands.Context,
			location: str,
			destination: str,
			time: str,
			*,
			flags: CreatingConvoyFlags
	):
		"""
		Arguments:
			location: str - a city name to start
			destination: str - a city name to finish
			time: str - it is recommended to use dd.mm.yy hh:mm format and
			specify a time zone.
		"""
		await self.translator.installBindedLanguage(ctx.guild.id)
		reply_embed = SuccessEmbed(title=self.translator("Convoy")).add_field(
			name=self.translator("Description"),
			value=self.translator("Location: ") + location + "\n" + self.translator(
			"Destination: ") + destination + "\n" + self.translator("Time: ") + time
		)
		information_field_value: List[str] = []
		if flags.rest:
			information_field_value.append(self.translator("Rest: ") + flags.rest)
		if flags.map:
			information_field_value.append(self.translator("DLC maps: ") + flags.map)
		if flags.cargo:
			information_field_value.append(self.translator("Cargo: ") + flags.cargo)
		if information_field_value:
			reply_embed = reply_embed.add_field(name=self.translator("Information"),
			value="\n".join(information_field_value))
		if flags.extra_info:
			reply_embed = reply_embed.add_field(name=self.translator("Extra information"),
			value=flags.extra_info)
		if (vote_time := flags.vote):
			time_now = datetime.datetime.now(datetime.UTC)
			delta = datetime.timedelta(hours=vote_time.hour,
				minutes=vote_time.minute, seconds=vote_time.second)
			vote_to_time_as_object = time_now + delta
			vote_to_time = str(RelativeDiscordTimestamp(vote_to_time_as_object))
			reply_embed = reply_embed.add_field(
				name=self.translator("Vote information"),
				value=self.translator("Vote to") + " " +
				vote_to_time + "\n" +
				self.translator("accept_with_convoy")
			)
		current_message = await ctx.send(embed=reply_embed)
		if flags.vote:
			await current_message.add_reaction('✅')
			await current_message.add_reaction('❌')
			await asyncio.sleep(vote_time.second)
			current_message = await ctx.fetch_message(current_message.id)
			await self._totalVote(current_message, reply_embed)

	async def _totalVote(
		self,
		message: discord.Message,
		embed: discord.Embed
	) -> None:
		reactions = message.reactions
		yes_count, no_count = 0, 0
		for reaction in reactions:
			if str(reaction) == ":white_check_mark:":
				yes_count = reaction.count
			elif str(reaction) == ":x:":
				no_count = reactions.count
		if yes_count > no_count:
			value_for_vote_result_field = self.translator("convoy_accepted")
		elif yes_count == no_count:
			value_for_vote_result_field = self.translator("convoy_rejected_neutral")
		else:
			value_for_vote_result_field = self.translator("convoy_rejected")
		embed.set_field_at(
			-1,
			name=self.translator("vote_result"),
			value=value_for_vote_result_field
		)
		await message.edit(embed=embed)

async def setup(
	bot: BotConstructor # type: ignore[name-defined]
) -> None:
	await bot.add_cog(UserLog(bot, bot.dbconn, bot.context_provider))
	await bot.add_cog(Settings(bot, bot.dbconn, bot.i18n_translator))
	await bot.add_cog(ConvoyManager(bot, bot.dbconn, bot.i18n_translator))