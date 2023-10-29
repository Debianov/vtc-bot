"""
Модуль хранит основную логику всех пользовательских команд.
"""

from typing import Any, List, Tuple, Type, Union

import discord
import psycopg
from discord.ext import commands

from .converters import (
	Expression,
	SearchExpression,
	ShortSearchExpression,
	SpecialExpression
)
from .data import ActGroup, TargetGroup
from .exceptions import ExpressionNotFound, UnhandlePartMessageSignal
from .flags import UserLogFlags
from .main import BotConstructor
from .utils import ContextProvider


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
		Функция обработки ошибок. Является обработчиком discord.py.
		Обрабатывает все общие ошибки.

		Raises:
			error: если обработка исключения error не предусмотрена.
		"""
		if isinstance(error, commands.BadUnionArgument):
			await ctx.send("Убедитесь, что вы указали существующие "
				"объекты\"{}\" в параметре {}, и у меня есть к ним доступ.".format(
				error.errors[0].argument, error.param.name)) # type: ignore
		elif isinstance(error, commands.MissingRequiredArgument):
			current_parameter = error.param.name
			await ctx.send(f"Убедитесь, что вы указали все обязательные "
				"параметры. Не найденный параметр:"
				f" {current_parameter}")
		elif isinstance(error.original, UnhandlePartMessageSignal): # type: ignore
			# данная ошибка передаётся только через атрибут original
			await ctx.send("Убедитесь, что вы указали флаги явно, либо "
				"указали корректные данные."
				f" Необработанная часть сообщения: {ctx.current_argument}")
		else:
			raise error

	@commands.group(aliases=["logs"], invoke_without_command=True)
	async def log(self, ctx: commands.Context) -> None:
		"""
		Команда предоставляет подкоманды, реализующие управление логированием.
		"""
		await ctx.send("Убедитесь, что вы указали подкоманду.")

	@log.command(aliases=["1", "cr"]) # type: ignore[arg-type]
	async def create(
		self,
		ctx: commands.Context,
		target: commands.Greedy[Union[discord.TextChannel,
			discord.Member, discord.CategoryChannel, SearchExpression]],
		act: Union[ShortSearchExpression[ActGroup], str], # type: ignore [type-arg]
		d_in: commands.Greedy[Union[discord.TextChannel,
			discord.Member, SearchExpression, SpecialExpression]],
		*,
		flags: UserLogFlags
	) -> None:
		"""
		Подкоманда для создания и записи цели, действия которой нужно логировать.

		Аргументы:
			target (упоминание, SearchExpression): за кем/чем следить.
			act (ShortSearchExpression, название/ID действия):
			какие действия отслеживать.
			d_in (упоминание канала/пользователя, SearchExpression, df/default):
			куда отправлять логи. Если df\
			— то в установленный по умолчанию объект.
		"""
		if not ctx.guild:
			return None

		self.context_provider.updateContext(ctx.guild)

		initial_target = self.removeNesting(target)
		initial_act = self.removeNesting(act) #!
		initial_d_in = self.removeNesting(d_in)

		if not d_in: # если пропускается последний обязательный параметр
			# — ошибка не выводится, поэтому приходится выкручиваться.
			raise commands.MissingRequiredArgument(ctx.
				command.clean_params["d_in"]) # type: ignore [union-attr]
		else:
			await self.checkForUnhandleContent(ctx, initial_target or target,
				initial_act or act, initial_d_in or d_in, flags.name,
				flags.output, flags.priority, flags.other)

		target_instance = TargetGroup(
			self.dbconn,
			ctx.guild.id,
			target=target, # type: ignore [arg-type]
			act=act, # type: ignore [arg-type]
			d_in=d_in # type: ignore [arg-type]
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

	async def checkForUnhandleContent(
		self,
		ctx: commands.Context,
		*parameters: Any
	) -> None:
		r"""
		Для проверки на необработанный контент. Основан на сравнении
		`ctx.current_argument <https://discordpy.readthedocs.io/en/
		stable/ext/commands/api.html?highlight=ctx%20
		current_argument#discord.ext.commands.Context.current_argument>`_
		обработанного аргумента со всеми параметрами.

		Args:
			\*parameters (Any): все распарсенные параметры из команды.

		Raises:
			UnhandlePartMessageSignal: вызывается при обнаружении необработанного\
			элемента.
		"""
		if not ctx.current_argument:
			return
		current_argument = ctx.current_argument.split(
			" ") # discord.py останавливается на
		# необработанном аргументе, если ни один из конвертеров не подошёл.
		for (ind, maybe_argument) in enumerate(current_argument[:]):
			if maybe_argument.startswith("-"):
				current_argument.remove(maybe_argument)
			elif maybe_argument.startswith("<") and maybe_argument.\
				endswith(">"):
				converter = commands.ObjectConverter()
				discord_object = await converter.convert(ctx, maybe_argument)
				current_argument[ind] = str(discord_object.id)
			# второй раз проверяю, поскольку других методов игнорирования
		if self.checkExpressions(current_argument):
			# верных expression-ов не нашёл.
			return
		ready_check_parameters: List[str] = []
		for element in parameters:
			if hasattr(element, "id"):
				ready_check_parameters.append(str(element.id))
			elif isinstance(element, list):
				for d_id in map(lambda x: str(x.id), element):
					ready_check_parameters.append(d_id)
			else:
				ready_check_parameters.append(element)
		for argument in current_argument:
			if argument not in ready_check_parameters:
				raise UnhandlePartMessageSignal(ctx.current_argument)

	def removeNesting(self, instance: Any):
		"""
			Функция для удаления вложенностей.

			Returns:
				Optional[List[discord.abc.Messageable]]
		"""
		if len(instance) == 1 and isinstance(instance[0], list):
			tmp = instance[0]
			instance.remove(tmp)
			instance.extend(tmp)

	def checkExpressions(self, maybe_expressions: List[str]) -> bool:
		"""
		Команда для проверки текста на все возможные Expression.

		Returns:
			bool
		"""
		expression_classes: Tuple[Type[Expression], ...] = (
			SearchExpression, ShortSearchExpression, SpecialExpression
		)
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

async def setup(
	bot: BotConstructor, # type: ignore [name-defined]
) -> None:
	await bot.add_cog(UserLog(bot, bot.dbconn, bot.context_provider))