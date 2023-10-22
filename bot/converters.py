"""
Модуль хранит конвертеры, необходимый для парсинга команд.
"""
from typing import List, Optional, Type, Union

import discord
from discord.ext import commands

from ._types import DiscordGuildObjects
from .data import DiscordObjectsGroupAnalyzator, DiscordObjectsGroup
from .exceptions import (
	SearchExpressionNotFound,
	ShortSearchExpressionNotFound,
	SpecialExpressionNotFound
)


class Expression(commands.Converter):
	"""
	Абстрактный класс объектов, реализующих выражения.
	"""

	async def convert(self, ctx: commands.Context, argument: str):
		"""
		Вызывается автоматически discord.py. Переопределённный метод класса
		`commands.Converter <https://discordpy.readthedocs.io/en/stable/ext/\
		commands/api.html?highlight=help#discord.ext.commands.Converter>`_.
		"""
		pass

	def checkExpression(self, argument: str) -> None:
		"""
		Проверяет выражение с точки зрения синтаксиса.
		"""
		pass

class SearchExpression(Expression):
	"""
	Класс, реализующий выражение поиска.

	Examples:
		usr:* — передача всех пользователей в текущем контексте.
	"""

	async def convert(
		self,
		ctx: commands.Context,
		argument: str
	) -> List[DiscordGuildObjects]:
		self.argument = argument
		self.checkExpression()
		self.string: List[str] = argument.split(":")
		self.result: List[Union[discord.abc.GuildChannel, discord.abc.Member]] = []
		self.ctx = ctx
		self.extractDataGroup()
		self.analyzeWildcard()
		return self.result

	def checkExpression(self, argument: Optional[str] = None) -> None:
		"""
		Проверяет выражение с точки зрения синтаксиса. Данный метод подлежит\
		вызову вне аннотаций команд для проверки других аргументов в обход convert.

		Args:
			argument: передаётся, если вызывается вручную не в контексте парсинга.
		"""
		if not argument:
			argument = self.argument
		if argument.find(":") == -1:
			raise SearchExpressionNotFound(argument)

	def extractDataGroup(self) -> None:
		"""
		Метод для определения :class:`DataGroup`.

		Raises:
			SearchExpressionNotFound: возбуждается при отсутствии подходящих DataGroup.
		"""
		self.data_groups: List[DiscordObjectsGroup] = DiscordObjectsGroupAnalyzator(
			self.ctx, self.string[0]).analyze()
		if not self.data_groups:
			raise SearchExpressionNotFound(self.argument)

	def analyzeWildcard(self) -> None:
		"""
		Метод для извлечения информации из :class:`DataGroup`.
		"""
		for data_group in self.data_groups:
			if self.string[1] == "*":
				self.result += data_group.extractData()

class ShortSearchExpression(Expression):
	r"""
	Класс представляет реализацию короткого поискового выражения —
	аналога :class:`SearchExpression`, но без явного указания
	:class:`DataGroup`.

	Examples:
		\* — передача всех объектов.
	"""

	# def __init__(self) -> None:
	# 	self.data_group: Union[Type[DiscordObjectsGroup], DiscordObjectsGroup]  = DiscordObjectsGroup

	@classmethod
	def __class_getitem__(
		cls,
		default_data_group: Type[DiscordObjectsGroup] = DiscordObjectsGroup,
	) -> Type['ShortSearchExpression']:
		"""
		Args:
			default_data_group (DiscordObjectsGroup): один из объектов
			:class:`DataGroup`, который использоваться для выполнения wildcard.
		"""
		cls = cls()
		cls.data_group = default_data_group
		return cls

	async def convert(
		self,
		ctx: commands.Context,
		argument: str
	) -> List[DiscordGuildObjects]:
		self.checkExpression(argument)
		self.string: str = argument # type: ignore
		self.result: List[DiscordGuildObjects] = []
		self.analyzeWildcard(ctx=ctx)
		return self.result
	
	def checkExpression(self, argument: str) -> None:
		if not argument == "*":
			raise ShortSearchExpressionNotFound(argument)

	def analyzeWildcard(self, **args_to_extract_method) -> None:
		if self.string == "*":
			self.result += self.data_group.extractData(**args_to_extract_method)

class SpecialExpression(Expression):
	"""
	Класс представляет специальное выражение, которое является
	специальным именем и характеризует какую-либо опцию.

	Examples:
		df — передача дефолтного объекта из настроек.
	"""

	async def convert(self, ctx: commands.Context, argument: str) -> str:
		self.checkExpression(argument)
		return argument

	def checkExpression(self, argument: str) -> None:
		if argument not in ["df", "default"]:
			raise SpecialExpressionNotFound(argument)