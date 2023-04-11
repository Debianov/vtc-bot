import discord
from discord.ext import commands
from typing import List, Optional, Any, Union

from .data import DataGroupAnalyzator, DiscordObjectsGroup
from .exceptions import SearchExpressionNotFound

class SearchExpression(commands.Converter):

	async def convert(self, ctx: commands.Context, argument: str) -> Union[List[discord.abc.Messageable], None]:
		if argument.find(":") == -1:
			raise commands.SearchExpressionNotFound(argument)
		self.string: List[str] = argument.split(":")
		self.result: List[discord.Messageable] = []
		self.ctx = ctx

		self.extractDataGroup()
		self.analyzeWildcard()
		return self.result

	def extractDataGroup(self) -> None:
		self.data_groups: List[DiscordObjectsGroup] = DataGroupAnalyzator(self.ctx, self.string[0]).analyze()

	def analyzeWildcard(self) -> None:
		for data_group in self.data_groups:
			if self.string[1] == "*":
				self.result += data_group.extractData()