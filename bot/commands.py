import discord
from discord.ext import commands
from typing import Optional, Union, Tuple, List, Any, Final
import asyncio
from datetime import timedelta

from .flags import *
from .converters import SearchExpression, ShortSearchExpression, SpecialExpression
from .data import *
from .config import bot

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
# TODO ошибка при написании дальше параметров без указания флагов.
async def create(
	ctx: commands.Context,
	target: commands.Greedy[Union[discord.TextChannel, discord.Member, discord.CategoryChannel, SearchExpression]],
	act: Union[ShortSearchExpression[ActGroup], str],
	d_in: commands.Greedy[Union[discord.TextChannel, discord.Member, SearchExpression, SpecialExpression]] = commands.command(name="in"),
	*,
	flags: UserLogFlags
) -> None:
	target_instance = TargetGroup(ctx)
	target_instance.target = target
	target_instance.act = act
	
	if target_instance.d_in in ["df", "default"]:
		pass # TODO Special для этого есть.
	target_instance.d_in = d_in

	for key in flags.get_flags().keys():
		if flags.__dict__[key]:
			setattr(target_instance, key, flags.__dict__[key])

	coincidence_targets_instance = await TargetGroup.extractData(ctx.guild, target=target_instance.target, act=target_instance.act, 
	d_in=target_instance.d_in, name=target_instance.name)
	if coincidence_targets_instance:
		coincidence_target = coincidence_targets_instance[0]
		await ctx.send(f"Цель с подобными параметрами уже существует: {coincidence_target.id} ({coincidence_target.name})"
		f". Совпадающие элементы: {target_instance.getCoincidenceTo(coincidence_target)}") # TODO вывод доработать.
		# TODO подумать над уникальностью name.
	else:
		await target_instance.writeData()
		await ctx.send("Цель добавлена успешно.")