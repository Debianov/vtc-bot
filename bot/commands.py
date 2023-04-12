import discord
from discord.ext import commands
from typing import Optional, Union, Tuple, List, Any, Final

from .flags import *
from .converters import SearchExpression, ShortSearchExpression, SpecialExpression
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
		# TODO склонение + убрать пинг при упоминании, если возможно.
		await ctx.send("Убедитесь, что вы указали существующие объекты \"{}\" в параметре {}, и у меня есть к ним доступ.".format(
			error.errors[0].argument, error.param.name))
	else:
		raise error

@bot.group(aliases=["logs"], invoke_without_command=True)
async def log(ctx: commands.Context) -> None:
	await ctx.send("Убедитесь, что вы указали пункт меню.")

@log.command(aliases=["1", "cr"])
#? походу у типов с упоминанием нет поддержки группировки через кавычки.
# int и str работает только, а вот TextChannel и ост. подобные — нет.
#! пока ситуация такая, что target и d_in приходится делать жадным, а 
# act приходится работать через группировку (если сделать act жадным
# он начинает кушать в том числе упоминания из d_in, но это уже другая история).
# TODO походу надо делать свои конвертеры + завести на существующих
# группировку тоже.
async def create(
	ctx: commands.Context,
	target: commands.Greedy[Union[discord.TextChannel, discord.Member, discord.CategoryChannel, SearchExpression]],
	act: Union[ShortSearchExpression[ActGroup], int, str],
	d_in: commands.Greedy[Union[discord.TextChannel, discord.Member, SearchExpression, SpecialExpression]] = commands.command(name="in"),
	*,
	flags: UserLogFlags
) -> None:
	target_instance = TargetGroup()
	target_instance.writeData("target", target) #? проверку данных лучше может осуществлять в writeData?
	target_instance.writeData("act", act) # act нужно проверить, чтоб он состоял только из цифр/букв, например.
	
	if "".join(d_in) in ["df", "default"]: #? откуда в d_in берётся список, когда я в конвертере ничего не писал?
		# TODO извлечение дефолтного канала из настроек и присвоение d_in.
		target_instance.writeData("in", d_in)

	for key in flags.get_flags().keys():
		if flags.__dict__[key]:
			target_instance.writeData(key, flags.__dict__[key])