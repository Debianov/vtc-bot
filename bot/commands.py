import discord
from discord.ext import commands
from typing import Optional, Union, Tuple, List, Any, Final

from .flags import *
from .converters import SearchExpression
from .data import *

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(
	command_prefix="sudo ",
	intents=intents
)

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
	if isinstance(error, commands.BadUnionArgument):
		# TODO склонение
		await ctx.send("Убедитесь, что вы указали существующие объекты \"{}\" в параметре {}, и у меня есть к ним доступ.".format(
			error.errors[0].argument, error.param.name))
	else:
		raise error

@bot.group(aliases=["logs"], invoke_without_command=True)
async def log(ctx: commands.Context) -> None:
	await ctx.send("Убедитесь, что вы указали пункт меню.")

@log.command(aliases=["1", "cr"])
async def create(
	ctx: commands.Context,
	target: commands.Greedy[Union[discord.TextChannel, discord.Member, discord.CategoryChannel, SearchExpression]],
	act: Union[str, int],
	d_in: commands.Greedy[Union[discord.TextChannel, discord.Member, SearchExpression]],
	*,
	flags: UserLogFlags
) -> None:
	target_instance = TargetGroup()
	target_instance.writeData("target", target)

	# target.writeData("act", act)

	# if not d_in:
	# 	raise commands.BadArgument(exist_object_error_text.format("TODO", "in"))
	# D_in(d_in).writeToDB()

	# error_message = ErrorMessage()
	# await ctx.send(error_message.gatherError())
	# try:
	# 	DiscordObjectValidator(target, ctx).validate()
	# except DiscordObjectDoesNotExist as error:
	# 	await ctx.send(error.getTextError().format(ctx.args[1], "target"))