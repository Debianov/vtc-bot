import discord
from discord.ext import commands
from typing import List, Optional, Any, Final, Callable, Tuple, Union, Type, Dict
import psycopg

__all__ = (
	"DataGroupAnalyzator",
	"DataGroup",
	"UserGroup",
	"ChannelGroup",
	"ActGroup",
	"TargetGroup",
	"initDB"
)

aconn: Optional[psycopg.AsyncConnection[Any]] = None

async def initDB() -> None:
	global aconn
	with open("db_secret.sec") as text:
		aconn = await psycopg.AsyncConnection.connect("dbname={} user={}".format(text.readline(), 
		text.readline()))
	aconn.adapters.register_dumper(discord.abc.Messageable, DiscordObjectsDumper)
	aconn.adapters.register_loader("text", DiscordObjectsLoader)

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

	def extractData(self, d_id: Optional[str] = None) -> List[discord.Member]:
		if not d_id:
			return self.ctx.guild.members

class ChannelGroup(DiscordObjectsGroup):

	USER_IDENTIFICATOR: str = "ch"

	def extractData(self, d_id: Optional[str] = None) -> List[discord.abc.GuildChannel]:
		if not d_id:
			return self.ctx.guild.channels

class DBObjectsGroup(DataGroup):
	pass

class ActGroup(DBObjectsGroup):

	DB_IDENTIFICATOR: str = "act"

	def extractData(self, coord: Optional[str] = None) -> List[str]:
		if not coord:
			pass
			# TODO извлекаем всю БД нахрен.
		return [""]

class TargetGroup(DBObjectsGroup):

	DB_IDENTIFICATOR: str = "target"

	def __init__(self) -> None:
		self.target: Union[discord.TextChannel, discord.Member, discord.CategoryChannel, None] = None
		self.act: Union[int, str, None] = None # TODO act в ActGroup.
		self.d_in: Union[discord.TextChannel, discord.Member, None] = None
		self.name: Union[str, int, None] = None
		self.output: Union[str, int, None] = None
		self.priority: Union[int, None] = None
		self.other: Union[str, int, None] = None

	def register(self, parameter: str, value: Optional[str]) -> None:
		if parameter in self.__dict__.keys():
			self.__dict__[parameter] = value
		else:
			raise AttributeError(parameter)

	async def writeData(self) -> None:
		async with aconn.cursor() as acur:
			await acur.execute("""
					INSERT INTO target VALUES (%s, %s, %s, %s, %s, %s, %s);""", [self.target, self.act, self.d_in, self.name, self.output, self.priority, self.other])
			await aconn.commit()

class DiscordObjectsDumper(psycopg.adapt.Dumper):
	
	def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> str:
		if not isinstance(elem, discord.abc.Messageable) and not isinstance(elem, discord.abc.Connectable):
			return super().dump(elem)
		result: str = "DISCORD OBJECT" + " "
		for key in elem.__slots__:
			result += "{}:{}".format(key, getattr(elem, key)) + " "
		result = result.removesuffix(" ")
		return result.encode()

class DiscordObjectsLoader(psycopg.adapt.Loader):

	def load(self, data: str) -> Union[discord.abc.Messageable, discord.abc.Connectable]:
		if not data.startswith("DISCORD OBJECT"):
			return super().load(data)
		
		data.removeprefix("DISCORD OBJECT ")
		split_data: List[str] = data.split(" ")
		dict_data: Dict[str, str] = {}

		for (key, value) in zip(split_data[::2], split_data[1::2]):
			dict_data[key] = value
		instance = discord.Member(data=dict_data.pop("data"), guild=dict_data.pop("guild"), state=dict_data.pop("state"))
		for (key, value) in dict_data.items():
			setattr(instance, key, value)
		
		return instance