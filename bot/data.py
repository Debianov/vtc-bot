#? что с кешированием?
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

context: Union[Type["discord.Guild"], Type["discord.Bot"], None] = None # нужно передавать объект бота
# для корректной работы loader.

async def initDB() -> None:
	global aconn
	with open("db_secret.sec") as text:
		aconn = await psycopg.AsyncConnection.connect("dbname={} user={}".format(text.readline(), 
		text.readline()))
	aconn.adapters.register_dumper(discord.abc.Messageable, DiscordObjectsDumper)
	aconn.adapters.register_loader("bigint[]", DiscordObjectsLoader)

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

	def __init__(
		self, 
		ctx: Union[discord.Guild, discord.Client], 
		target: Union[discord.TextChannel, discord.Member, discord.CategoryChannel, None] = None, 
		act: Union[int, str, None] = None,
		d_in: Union[discord.TextChannel, discord.Member, None] = None,
      name: Union[str, int, None] = None,
      output: Union[str, int, None] = None,
      priority: Union[int, None] = None,
      other: Union[str, int, None] = None
	) -> None:
		self.ctx = ctx
		self.target = target
		self.act  = act # TODO act в ActGroup (подумать).
		self.d_in = d_in
		self.name = name
		self.output = output
		self.priority = priority
		self.other = other

	def __iter__(self):
		return iter([self.target, self.act, self.d_in, self.name, self.output, self.priority, self.other])

	def __setattr__(
		self, 
		name: str, 
		nvalue: Optional[str]
	) -> None:
		if nvalue:
			match name:
				case "act":
					checking_nvalue = str(nvalue).replace(" ", "")
					if not checking_nvalue.isalpha():
						if not checking_nvalue.isdigit():
							raise ValueError(name, nvalue)
				case "name":
					if not str(nvalue).isprintable():
						raise ValueError(name, nvalue)
		super().__setattr__(name, nvalue)

	async def writeData(self) -> None:
		async with aconn.cursor() as acur:
			# TODO вписывать id гильдии.
			await acur.execute("""
					INSERT INTO target VALUES (%s, %s, %s, %s, %s, %s, %s);""", [self.target, self.act, self.d_in, self.name, self.output, self.priority, self.other])
			await aconn.commit()

	@classmethod
	async def extractData(
		cls: 'TargetGroup', 
		ctx: Union[discord.Guild, discord.Client], 
		coord: Optional[str] = None, 
		condition: Optional[str] = None
	) -> List['TargetGroup']:
		global context
		async with aconn.cursor() as acur:
			context = ctx # пока приходится так. Нужно найти способ, как передать в load контекст.
			if coord and condition:
				await acur.execute("""
						SELECT %s FROM target WHERE %s;""", [coord, condition])
			elif coord and condition is None:
				await acur.execute("""
						SELECT %s FROM target;""", [coord])
			elif coord is None and condition:
				pass
			else:
				await acur.execute("""
						SELECT * FROM target;""") # TODO нужно будет сделать фильтрацию по гильдиям.
			result: List[TargetGroup] = []
			for row in await acur.fetchall():
				result.append(cls(ctx, row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
			return result

class DiscordObjectsDumper(psycopg.adapt.Dumper):
	
	def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> bytes:
		if not isinstance(elem, discord.abc.Messageable) and not isinstance(elem, discord.abc.Connectable):
			return super().dump(elem)
		return str(elem.id).encode()

class DiscordObjectsLoader(psycopg.adapt.Loader):

	def load(self, data: bytes) -> Union[discord.abc.Messageable, discord.abc.Connectable]: 
		#? есть варианты, как передавать в load context через параметр?
		string_data: str = data.decode()
		for attr in ('get_member', 'get_user', 'get_channel'):
			try:
				instance = getattr(context, attr)(int(string_data))
			except (discord.DiscordException, AttributeError):
				continue
			else:
				break
		return instance