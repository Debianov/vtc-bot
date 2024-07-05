"""
The module for parsing the user commands with converters that support
discord.py.
"""
import abc
from typing import Generic, List, Type, TypeVar, Union

import discord
from discord.ext import commands

from ._types import DiscordGuildObjects
from .data import DataGroupAnalyzator, DiscordObjectsGroup
from .exceptions import (
	SearchExpressionNotFound,
	ShortSearchExpressionNotFound,
	SpecialExpressionNotFound
)

T = TypeVar("T")


class Expression(commands.Converter, metaclass=abc.ABCMeta):
	"""
	The abstract class of objects that implement the expression mechanism.
	"""

	@abc.abstractmethod
	async def convert(self, ctx: commands.Context, argument: str):
		"""
		Overridden method of the `commands.Converter <https://discordpy.read\
		thedocs.io/en/stable/ext/commands/api.html?highlight=help#discord.\
		ext.commands.Converter>`_ class.
		"""
		raise NotImplementedError()

	@abc.abstractmethod
	def _checkExpression(self, maybe_expression: str):
		"""
		Checks the syntax expression.
		"""
		raise NotImplementedError()

class SearchExpression(Expression):
	"""
	This class implements search expressions.

	Examples:
		usr:* — all users.
	"""

	async def convert(
		self,
		ctx: commands.Context,
		argument: str
	) -> List[DiscordGuildObjects]:
		self._checkExpression(argument)
		self.argument = argument
		self.group_identif: str = self.split_argument[0]
		self.wildcard: str = self.split_argument[1]
		self.result: List[Union[discord.abc.GuildChannel, discord.abc.Member]] = []
		self.ctx = ctx
		self._extractDataGroup()
		self._analyzeWildcard()
		return self.result

	def _checkExpression(self, maybe_expression: str) -> None:
		"""
		"""
		self.split_argument = maybe_expression.split(":")
		if maybe_expression.find(":") == -1 or len(self.split_argument) > 2:
			raise SearchExpressionNotFound(maybe_expression)

	def _extractDataGroup(self) -> None:
		"""
		The method to get the :class:`DataGroup` instance.

		Raises:
			SearchExpressionNotFound: raised when any expressions don't
			match.
		"""
		self.data_groups: List[DiscordObjectsGroup] = DataGroupAnalyzator(
			self.ctx, self.group_identif).analyze()
		if not self.data_groups:
			raise SearchExpressionNotFound(self.argument)

	def _analyzeWildcard(self) -> None:
		"""
		The method to get the db information from the :class:`DataGroup`
		instance.
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
		self._checkExpression(argument)
		self.wildcard: str = argument # type: ignore
		self.result: List[DiscordGuildObjects] = []
		self._analyzeWildcard()
		return self.result
	
	def _checkExpression(self, maybe_expression: str) -> None:
		if not maybe_expression == "*":
			raise ShortSearchExpressionNotFound(maybe_expression)

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
		self._checkExpression(argument)
		return argument

	def _checkExpression(self, maybe_expression: str) -> None:
		if maybe_expression not in ["df", "default"]:
			raise SpecialExpressionNotFound(maybe_expression)