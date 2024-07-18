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
from .exceptions import UnhandlePartMessageSignal
from .flags import UserLogFlags
from .main import BotConstructor
from .utils import ContextProvider, removeNesting

logger = logging.getLogger(__name__)

class UserLog(commands.Cog):

	def __init__(
		self,
		bot: commands.Bot,
		dbconn: psycopg.AsyncConnection[Any],
		context_provider: ContextProvider
	) -> None:
		self.bot = bot
		self.dbconn: psycopg.AsyncConnection[Any] = dbconn
		self.context_provider: ContextProvider = context_provider
		bot.on_command_error = self._on_command_error # type: ignore [method-assign]

	async def _on_command_error(
		self,
		ctx: commands.Context,
		error: commands.CommandError
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