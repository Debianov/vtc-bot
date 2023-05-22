# TODO Вместо __all__ лучше будет импортировать списком в самом модуле

import discord
from discord.ext import commands
from typing import Optional, Union, Tuple, List, Any, Final
import asyncio
from datetime import timedelta

from .flags import *
from .converters import Expression, SearchExpression, ShortSearchExpression, SpecialExpression
from .exceptions import ExpressionNotFound
from .data import *
from .config import bot

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
	#!якорь: выводит разные ошибки, но не до конца. Так, например, при выводе sudo log 1 hfg:* 43 usr:*
	# сразу крашит в нужную ошибку (хоть и описание не правильное). При выводе log 1 hfg:* 43 улетает 
	# unhandle, хотя также не хватает недостающего параметра, а все raise в конвертерах дописаны.
	if isinstance(error, commands.BadUnionArgument):
		# TODO склонение + убрать пинг при упоминании, если возможно.
		await ctx.send("Убедитесь, что вы указали существующие объекты \"{}\" в параметре {}, и у меня есть к ним доступ.".format(
			error.errors[0].argument, error.param.name))
	elif isinstance(error, commands.MissingRequiredArgument):
		params = list(ctx.command.clean_params.keys())
		if len(ctx.args[1]) == 0: # если список обработанных аргументов пустой, значит никакой из аргументов 
			# не был указан впринципе (в контексте текущего исключения). 
			# discord.py почему-то кидает ошибку с пропущенным act когда пропущен 
			# самый первый аргумент — target.
			missing_parameters = params
		else:
			current_parameter = error.param.name
			# TODO бажочек: если определяется параметр по серединке (в порядке сигнатуры),
			# то пропущенные параметры до него не указываются.
			missing_parameters = params[params.index(current_parameter):]
				# flags — всегда необязательные
		missing_parameters = list(filter(lambda x: x != "flags", missing_parameters)) 
		await ctx.send(f"Убедитесь, что вы указали все обязательные параметры. Не найденный/(е) параметр/(ы):"
			f" {', '.join(missing_parameters)}") # TODO склонения.
	else:
		raise error

@bot.group(aliases=["logs"], invoke_without_command=True)
async def log(ctx: commands.Context) -> None:
	await ctx.send("Убедитесь, что вы указали подкоманду.")

@log.command(aliases=["1", "cr"])
#? походу у типов с упоминанием нет поддержки группировки через кавычки.
# int и str работает только, а вот TextChannel и ост. подобные — нет.
#! пока ситуация такая, что target и d_in приходится делать жадным, а 
# act приходится работать через группировку (если сделать act жадным
# он начинает кушать в том числе упоминания из d_in, но это уже другая история).
# TODO походу надо делать свои конвертеры + завести на существующих
# группировку тоже.
# TODO ошибка при написании дальше параметров без указания флагов.
# TODO d_in в сравнении при поиске совпадений убрать, наверн.
async def create(
	ctx: commands.Context,
	target: commands.Greedy[Union[discord.TextChannel, discord.Member, discord.CategoryChannel, SearchExpression]],
	act: Union[ShortSearchExpression[ActGroup], str],
	d_in: commands.Greedy[Union[discord.TextChannel, discord.Member, SearchExpression, SpecialExpression]],
	*,
	flags: UserLogFlags
) -> None:

	initial_target = removeNesting(target)
	initial_act = removeNesting(act)
	initial_d_in = removeNesting(d_in)

	await checkForUnhandleContent(ctx, initial_target or target, initial_act or act,
	initial_d_in or d_in, flags.name, flags.output, flags.priority, flags.other)

	if not d_in: # если пропускается последний обязательный параметр — ошибка не выводится, поэтому приходится
		# выкручиваться.
		raise commands.MissingRequiredArgument(ctx.command.clean_params["d_in"])

	target_instance = TargetGroup(ctx)
	target_instance.target = target
	target_instance.act = act # TODO всегда должен идти список.
	
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

async def checkForUnhandleContent(ctx: commands.Context, *parameters: Any) -> None:
	current_argument = ctx.current_argument.split(" ") # discord.py останавливается на
	# необработанном аргументе, если ни один из конвертеров не подошёл.
	for (ind, maybe_argument) in enumerate(current_argument[:]):
		if maybe_argument.startswith("-"):
			current_argument.remove(maybe_argument)
		elif maybe_argument.startswith("<") and maybe_argument.\
			endswith(">"):
			converter = commands.ObjectConverter()
			discord_object = await converter.convert(ctx, maybe_argument)
			current_argument[ind] = str(discord_object.id)
	if checkExpressions(current_argument): # второй раз проверяю, поскольку других методов игнорирования
		# верных expression-ов не нашёл.
		return
	ready_check_parameters: List[str] = []
	for element in parameters:
		if isinstance(element, discord.abc.Messageable):
			ready_check_parameters.append(str(element.id))
		elif isinstance(element, list):
			for d_id in map(lambda x: str(x.id), element):
				ready_check_parameters.append(d_id)
		else:
			ready_check_parameters.append(element)
	for argument in current_argument:
		if not argument in ready_check_parameters:
			await ctx.send("Убедитесь, что вы указали флаги явно, либо указали корректные данные."
				f" Необработанная часть сообщения: {ctx.current_argument}")
			# TODO можно интерактив подвезти.
			raise commands.CommandError(f"message_part {ctx.current_argument} unhandle")

def removeNesting(instance: List[Any])\
	-> Optional[List[discord.abc.Messageable]]:
	if len(instance) == 1 and isinstance(instance[0], list):
		tmp = instance[0]
		instance.remove(tmp)
		instance.extend(tmp)

def checkExpressions(maybe_expressions: List[str]) -> bool:
	expression_classes = (SearchExpression, ShortSearchExpression, SpecialExpression) # TODO
	# сделать метод с проходам по иерархия классов, когда (если) у меня разрастётся converters.
	for argument in maybe_expressions:
		for d_class in expression_classes:
			instance = d_class()
			try:
				instance.checkExpression(argument)
			except ExpressionNotFound:
				continue
			else:
				return True
	return False