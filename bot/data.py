"""
Модуль хранит классы для работы с БД.
"""

import discord
from discord.ext import commands
from typing import List, Optional, Any, Final, Callable, Tuple, Union, Type, Dict, Set
import psycopg

class DiscordObjectsDumper:
	"""
	Преобразовывает Discord-объекты в ID для записи в БД.
	"""

	def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> str:
		if isinstance(elem, commands.Context):
			return str(elem.guild.id).encode()
		return elem.id

class DiscordObjectsLoader:
	"""
	Преобразовывает записи из БД в объекты Discord.
	Не зарегестрирован как loader psycopg, поскольку технически не нашёл решения
	корректно без использования глобальных переменных
	"""

	def __init__(self, data: str):
		self.data = data

	def load(self, data: str, client: discord.Client)\
		-> Union[discord.abc.Messageable, discord.abc.Connectable, str]:
		string_data: str = data
		for attr in ('get_member', 'get_user', 'get_channel'):
			try:
				result: Optional[discord.abc.Messageable] = getattr(
					client, attr)(int(string_data))
				if result:
					return result
			except (discord.DiscordException, AttributeError):
				continue
		return string_data

class DataGroupAnalyzator:
	"""
	Класс реализует механизм определения :class:`DataGroup` по имени из str.
	"""
	
	def __init__(self, ctx: commands.Context, string: str) -> None:
		self.split_string: List[str] = string.split("+")
		self.relevant_groups: List[DataGroup] = []
		self.ctx = ctx

	def analyze(self) -> List['DiscordObjectsGroup']:
		"""
		Основной метод для определения :class:`DataGroup`.
		"""
		to_check: List[DiscordObjectsGroup] = DiscordObjectsGroup.__subclasses__()
		copy_string: List[str] = self.split_string
		for group_name in copy_string:
			for group_type in to_check:
				group_instance = group_type(self.ctx)
				if group_name == group_instance:
					self.relevant_groups.append(group_instance)
					break
		return self.relevant_groups

class DataGroup:
	"""
	Абстрактный класс объектов, реализующих доступ к данным.
	"""

	def extractData(self, d_id: Optional[str] = None) -> discord.abc.Messageable:
		pass

	def writeData(self) -> None:
		pass

class DiscordObjectsGroup(DataGroup):
	"""
	Абстрактный класс объектов, реализующих доступ к данным через Discord API.
	"""
	
	USER_IDENTIFICATOR: str = ""

	def __init__(self, ctx: commands.Context) -> None:
		self.ctx = ctx

	def __eq__(self, right_operand: Any) -> bool:
		return self.USER_IDENTIFICATOR == right_operand

class UserGroup(DiscordObjectsGroup):
	"""
	Класс реализует доступ к `discord.Member <https://discordpy.readthedocs.io/en/stable\
	/api.html?highlight=member#discord.Member>`_ в контексте гильдии.
	"""

	USER_IDENTIFICATOR: str = "usr"

	def extractData(self, d_id: Optional[str] = None) -> List[discord.Member]:
		if not d_id:
			return self.ctx.guild.members

class ChannelGroup(DiscordObjectsGroup):
	"""
	Класс реализует доступ к `discord.abc.Channel <https://discordpy.readthedocs.io/en/\
	stable/api.html?highlight=guildchannel#discord.abc.GuildChannel>`_ в контексте гильдии.
	"""

	USER_IDENTIFICATOR: str = "ch"

	def extractData(self, d_id: Optional[str] = None) -> List[discord.abc.GuildChannel]:
		if not d_id:
			return self.ctx.guild.channels

class DBObjectsGroup(DataGroup):
	"""
	Абстрактный класс объектов, реализующий доступ к данным через БД,
	а также их корректную запись.
	"""
	pass

class ActGroup(DBObjectsGroup):
	"""
	Класс реализует объект пользовательских действий.
	"""

	DB_IDENTIFICATOR: str = "act"

	def extractData(self, coord: Optional[str] = None) -> List[str]:
		if not coord:
			pass
		return [""]

class TargetGroup(DBObjectsGroup):
	"""
	Класс реализует объект цели логирования.
	"""

	DB_IDENTIFICATOR: str = "target"

	def __init__(
		self,		
		dbconn: psycopg.AsyncConnection[Any],
		ctx: command.Context,
		id: int = None,
		target: Optional[List[Union[discord.TextChannel, discord.Member, discord.CategoryChannel]]] = None,
		act: Union[str, None] = None,
		d_in: Optional[List[Union[discord.TextChannel, discord.Member]]] = None,
      name: Union[str, None] = None,
      output: Union[str, None] = None,
      priority: Union[int, None] = None,
      other: Union[str, None] = None
	) -> None:
		self.dbconn = dbconn
		self.id = id or self.generateID()
		self.ctx = ctx
		self.target = target
		self.act = act
		self.d_in = d_in
		self.name = name
		self.output = output
		self.priority = priority
		self.other = other

	def generateID(self) -> int:
		return 0

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
		async with self.dbconn.cursor() as acur:
			await acur.execute("""
					INSERT INTO target VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", [self.id, self.ctx, self.target, 
					self.act, self.d_in, self.name, self.output, self.priority, self.other])

	@classmethod
	async def extractData(
		cls: 'TargetGroup', 
		ctx: Union[discord.Guild, discord.Client],
		dbconn: psycopg.AsyncConnection[Any],
		placeholder: Optional[str] = "*",
		**object_parameters: Dict[str, Tuple[str, Any]]
	) -> List['TargetGroup']:
		"""
		Args:
			\**object_parameters: параметры, которые будут переданы в SQL запрос. Если\
			параметров несколько, то они объединяются через логический оператора OR.
		"""
		
		values_for_parameters: List[Any] = []
		query = [psycopg.sql.SQL(f"SELECT {placeholder} FROM target WHERE context_id = %s")]
		values_for_parameters.append(ctx.id)
		if object_parameters:
			parameters_query_part: List[psycopg.sql.SQL] = []
			for (parameter, value) in object_parameters.items():
				parameters_query_part.append(f"{parameter} = %s")
				values_for_parameters.append(value)
			query.append(psycopg.sql.SQL(f"AND ({(' OR ').join(parameters_query_part)})"))

		async with dbconn.cursor() as acur:
			await acur.execute(
				psycopg.sql.SQL(" ").join(query) + psycopg.sql.SQL(";"),
				values_for_parameters
			)
			result: List[TargetGroup] = []
			for row in await acur.fetchall():
				d_id, context_id, target, act, d_in, name, priority, output, other =\
				row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
				target = DiscordObjectsLoader(target).get_result()
				d_in = DiscordObjectsLoader(d_in).get_result()
				# result.append(cls(dbconn, row[1], row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
		return result

	def getComparableAttrs(self) -> List[Any]:
		"""
		Формирует сравниваемые атрибуты.

		Returns:
			List[Any]: список атрибутов, которые имеет смысл сравнивать с другими\
			экземплярами :class:`TargetGroup`.
		"""
		comparable_attrs: List[Any] = []
		objects_id: List[Any] = []
		for discord_objects in (self.target + self.d_in):
			objects_id.append(str(discord_objects.id))
		comparable_attrs += objects_id
		comparable_attrs.insert(len(self.target), self.act)
		comparable_attrs.append(self.name)
		return comparable_attrs

	def getCoincidenceTo(self, target: 'TargetGroup') -> str:
		"""
		Сравнить атрибуты с другим экземпляром :class:`TargetGroup` и вычислить точные совпадения.

		Returns:
			str: все совпавшие значения, перечисленных через запятую.
		"""
		current_attr: List[Any] = self.getComparableAttrs()
		compared_attr: List[Any] = target.getComparableAttrs()
		coincidence_attrs: List[Any] = []
		for current_attr in current_attr:
			if current_attr in compared_attr and current_attr is not None: # is not None — исключаем из проверки 
				# None-объекты, которые появляются только при отсутствии указания флага -name.
				coincidence_attrs.append(current_attr)
		return ", ".join(list(coincidence_attrs))

	def setCurrentContextForLoader(self, ctx):
		loader = self.dbconn.adapters.get_loader("bigint[]", psycopg.pq.Format(1))
		loader.ctx = ctx