import discord
from discord.ext import commands
from typing import List, Optional, Any, Final, Callable, Tuple, Union, Type

__all__ = (
	"DataGroupAnalyzator",
	"DataGroup",
	"UserGroup",
	"ChannelGroup",
	"ActGroup",
	"TargetGroup"
)

class DataGroupAnalyzator:
	
	def __init__(self, ctx: commands.Context, string: str) -> None:
		self.split_string: List[str] = string.split("+")
		self.definited_groups: List[DataGroup] = []
		self.ctx = ctx

	def analyze(self) -> List['DiscordObjectsGroup']:
		to_check: List[DiscordObjectsGroup] = DiscordObjectsGroup.__subclasses__()
		copy_string: List[str] = self.split_string
		for group_name in copy_string:
			for group_type in to_check:
				group_instance = group_type(self.ctx)
				if group_name == group_instance:
					self.definited_groups.append(group_instance)
					break
		return self.definited_groups

class DataGroup:

	def extractData(self, d_id: Optional[str] = None) -> discord.abc.Messageable:
		pass

	def writeData(self) -> None:
		pass

class DiscordObjectsGroup(DataGroup):
	
	USER_IDENTIFICATOR: str = ""

	def __init__(self, ctx: commands.Context) -> None:
		self.ctx = ctx

	def __eq__(self, right_operand: Any) -> bool:
		return self.USER_IDENTIFICATOR == right_operand

class UserGroup(DiscordObjectsGroup):

	USER_IDENTIFICATOR: str = "usr"

	def extractData(self, d_id: Optional[str] = None) -> discord.Member:
		if not d_id:
			return self.ctx.guild.members

class ChannelGroup(DiscordObjectsGroup):

	USER_IDENTIFICATOR: str = "ch"

	def extractData(self, d_id: Optional[str] = None) -> discord.abc.GuildChannel:
		if not d_id:
			return self.ctx.guild.members

class DBObjectsGroup(DataGroup):
	pass

class ActGroup(DBObjectsGroup):

	DB_IDENTIFICATOR: str = "act"

	def extractData(self) -> str:
		pass

class TargetGroup(DBObjectsGroup):

	DB_IDENTIFICATOR: str = "target"

	def __init__(self) -> None:
		# TODO создание объекта в БД.
		pass

	def writeData(self, parameter, value) -> None:
		# TODO запись в БД в строки объекта.
		print(parameter, value)