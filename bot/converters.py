from discord.ext import commands
from typing import List, Optional

from .data import DataGroupAnalyzator, DataGroup

class SearchExpression(commands.Converter):

	async def convert(self, ctx: commands.Context, argument: str) -> Optional['DataGroup']:
		self.string: List[str] = argument.split(":")
		self.extractDataGroup()
		self.analyzeWildcard()
		return self.data_group

	def extractDataGroup(self) -> None:
		self.data_group: DataGroup = DataGroupAnalyzator(self.string[0]).analyze()

	def analyzeWildcard(self) -> None:
		pass
		# if self.string[1] == "*":
		# 	self.data_group.extractFromDB() # TODO определиться, как будет
		# 	# передаваться изменения поведения при чтении из БД. Пока предлагается
		# 	# указывать как аргумент в функции, но как она будет обрабатываться там?
		# 	# Лучше передавать уже как какой-то готовый параметр, преобразованный
		# 	# из Wildcard, которые сможет понять объект БД.