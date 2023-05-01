#? что с кешированием?
import discord
from discord.ext import commands
from typing import List, Optional, Any, Final, Callable, Tuple, Union, Type, Dict, Set
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

async def initDB(
	dbname: str, 
	user: str
	) -> Optional[psycopg.AsyncConnection[Any]]:
	global aconn
	aconn = await psycopg.AsyncConnection.connect(f"dbname={dbname} user={user}", autocommit=True)
	aconn.adapters.discord_context: Union[Type["discord.Guild"], Type["discord.Bot"], None] = None
	aconn.adapters.register_dumper(discord.abc.Messageable, DiscordObjectsDumper)
	aconn.adapters.register_loader("bigint[]", DiscordObjectsLoader)
	return aconn

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
		ctx: Union[discord.Guild, discord.Client], # TODO посмотреть по разновидностям. 
		id: int = None,
		target: Optional[List[Union[discord.TextChannel, discord.Member, discord.CategoryChannel]]] = None, 
		act: Union[str, None] = None, # TODO преобразования из text в int, если isdigit.
		d_in: Optional[List[Union[discord.TextChannel, discord.Member]]] = None,
      name: Union[str, None] = None,
      output: Union[str, None] = None,
      priority: Union[int, None] = None,
      other: Union[str, None] = None
	) -> None:
		self.id = id or self.generateID()
		self.ctx = ctx
		self.target = target
		self.act  = act # TODO act в ActGroup (подумать).
		self.d_in = d_in
		self.name = name
		self.output = output
		self.priority = priority
		self.other = other

	def generateID(self) -> int:
		return 0 # TODO сделать нормальную генерацию ID.

	def __setattr__(
		self, 
		name: str, 
		nvalue: Optional[str]
	) -> None:
		if nvalue:
			match name:
				case "act":
					checking_nvalue = nvalue.replace(" ", "")
					if not checking_nvalue.isalpha():
						if not checking_nvalue.isdigit():
							raise ValueError(name, nvalue)
				case "name":
					if not nvalue.isprintable():
						raise ValueError(name, nvalue)
		super().__setattr__(name, nvalue)

	async def writeData(self) -> None:
		async with aconn.cursor() as acur:
			# TODO вписывать id гильдии.
			await acur.execute("""
					INSERT INTO target VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", [self.id, self.ctx, self.target, 
					self.act, self.d_in, self.name, self.output, self.priority, self.other])

	@classmethod
	async def extractData(
		cls: 'TargetGroup', 
		ctx: Union[discord.Guild, discord.Client], 
		placeholder: Optional[str] = "*", 
		**object_parameters: Dict[str, Tuple[str, Any]]
	) -> List['TargetGroup']:
		aconn.adapters.discord_context = ctx
		values_for_parameters: List[Any] = []
		query = [psycopg.sql.SQL(f"SELECT {placeholder} FROM target WHERE context_id = %s")]
		values_for_parameters.append(ctx.id)
		if object_parameters:
			parameters_query_part: List[psycopg.sql.SQL] = []
			for (parameter, value) in object_parameters.items():
				parameters_query_part.append(f"{parameter} = %s")
				values_for_parameters.append(value)
			query.append(psycopg.sql.SQL(f"AND ({(' OR ').join(parameters_query_part)})"))

		async with aconn.cursor() as acur:
			await acur.execute(
				psycopg.sql.SQL(" ").join(query) + psycopg.sql.SQL(";"),
				values_for_parameters
			)
			result: List[TargetGroup] = []
			for row in await acur.fetchall():
				result.append(cls(row[1], row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
		return result

	def getComparableAttrs(self) -> Set[Any]:
		comparable_attrs = set({str(self.act).lower(), str(self.name).lower()})
		objects_id = []
		for target in (self.target + self.d_in):
			objects_id.append(str(target.id))
		comparable_attrs.update(objects_id)
		return comparable_attrs

	def getCoincidenceTo(self, target: 'TargetGroup') -> str:
		# TODO метод сравнения прокачать.
		# TODO CASE WHEN как замена всему этому методу.
		# TODO SELECT Name, Price, Category, CASE WHEN Name LIKE '%Apple%' THEN 'Name Match' WHEN Price < 10 THEN 
		# 'Price Match' ELSE 'No Match' END AS Match_Condition FROM Products WHERE Name LIKE '%Apple%' OR Price < 10;
		current_attr: Set[Any] = self.getComparableAttrs()
		compared_attr: Set[Any] = target.getComparableAttrs()
		coincidence_attrs: Set[Any] = current_attr & compared_attr
		return ", ".join(list(coincidence_attrs))

class DiscordObjectsDumper(psycopg.adapt.Dumper):
	
	def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> bytes:
		if isinstance(elem, commands.Context):
			return str(elem.guild.id).encode()
		return str(elem.id).encode()

class DiscordObjectsLoader(psycopg.adapt.Loader):

	def load(self, data: bytes) -> Union[discord.abc.Messageable, discord.abc.Connectable]: 
		#? есть варианты, как передавать в load discord_context через параметр, а не aconn?
		string_data: str = data.decode()
		for attr in ('get_member', 'get_user', 'get_channel'):
			try:
				instance = getattr(aconn.adapters.discord_context, attr)(int(string_data))
			except (discord.DiscordException, AttributeError):
				continue
			else:
				break
		return instance