"""
Модуль хранит конвертеры, необходимый для парсинга команд.
"""
from typing import Generic, List, Optional, Type, TypeVar, Union

import discord
from discord.ext import commands

from ._types import DiscordGuildObjects
from .data import DataGroupAnalyzator, DiscordObjectsGroup
from .exceptions import (
	NoticeForDeveloper,
	SearchExpressionNotFound,
	ShortSearchExpressionNotFound,
	SpecialExpressionNotFound
)

T = TypeVar("T")

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
		raise NotImplementedError()

	def checkExpression(self, argument: str):
		"""
		Проверяет выражение с точки зрения синтаксиса.
		"""
		raise NotImplementedError()

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
		self.group_identif: str = self.split_argument[0]
		self.wildcard: str = self.split_argument[1]
		self.result: List[Union[discord.abc.GuildChannel, discord.abc.Member]] = []
		self.ctx = ctx
		self._extractDataGroup()
		self._analyzeWildcard()
		return self.result

	def checkExpression(self, argument: Optional[str] = None) -> None:
		"""
		Проверяет выражение с точки зрения синтаксиса. Данный метод подлежит\
		вызову вне аннотаций команд для проверки других аргументов в обход convert.

		Args:
			argument: передаётся, если вызывается вручную не в контексте парсинга.
		"""
		if not argument:
			try:
				argument = self.argument
			except AttributeError as excp:
				raise NoticeForDeveloper("self.argument doesn't exist because the"
				" convert method wasn't called. Call convert or pass argument.") from excp
		self.split_argument = argument.split(":")
		if argument.find(":") == -1 or len(self.split_argument) > 2:
			raise SearchExpressionNotFound(argument)

	def _extractDataGroup(self) -> None:
		"""
		Метод для определения :class:`DataGroup`.

		Raises:
			SearchExpressionNotFound: возбуждается при отсутствии подходящих DataGroup.
		"""
		self.data_groups: List[DiscordObjectsGroup] = DataGroupAnalyzator(
			self.ctx, self.group_identif).analyze()
		if not self.data_groups:
			raise SearchExpressionNotFound(self.argument)

	def _analyzeWildcard(self) -> None:
		"""
		Метод для извлечения информации из :class:`DataGroup`.
		"""
		if not self.wildcard == "*":
			raise SearchExpressionNotFound(self.argument)
		for data_group in self.data_groups:
			self.result += data_group.extractData()

class ShortSearchExpression(Expression, Generic[T]):
	r"""
	Класс представляет реализацию короткого поискового выражения —
	аналога :class:`SearchExpression`, но без явного указания
	:class:`DataGroup`.

	Examples:
		\* — передача всех объектов.
	"""

	data_group: Type[DiscordObjectsGroup] = DiscordObjectsGroup

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
		cls.data_group = default_data_group
		return cls

	async def convert(
		self,
		ctx: commands.Context,
		argument: str
	) -> List[DiscordGuildObjects]:
		self.data_group_instance = self.data_group(ctx)
		self.checkExpression(argument)
		self.wildcard: str = argument # type: ignore
		self.result: List[DiscordGuildObjects] = []
		self._analyzeWildcard()
		return self.result
	
	def checkExpression(self, argument: str) -> None:
		if not argument == "*":
			raise ShortSearchExpressionNotFound(argument)

	def _analyzeWildcard(self) -> None:
		if self.wildcard == "*":
			self.result += self.data_group_instance.extractData()

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