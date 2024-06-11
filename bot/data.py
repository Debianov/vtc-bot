"""
Модуль хранит классы для работы с БД.
"""

from typing import Any, Iterable, List, Optional, Sequence, Type, Union

import psycopg
from discord.ext import commands

from ._types import DiscordGuildObjects, IDObjects
from .attrs import TargetGroupAttrs


class DataGroupAnalyzator:
	"""
	Класс реализует механизм определения :class:`DiscordObjectsGroup`
	по имени из str.
	"""

	def __init__(self, ctx: commands.Context, string: str) -> None:
		self.split_string: List[str] = string.split("+")
		self.relevant_groups: List[DiscordObjectsGroup] = []
		self.ctx = ctx

	def analyze(self) -> List['DiscordObjectsGroup']:
		"""
		Основной метод для определения :class:`DiscordObjectsGroup`.
		"""
		to_check: List[Type[DiscordObjectsGroup]] =\
			DiscordObjectsGroup.__subclasses__()
		copy_string: List[str] = self.split_string
		for group_name in copy_string:
			for group_type in to_check:
				group_instance = group_type(self.ctx)
				if group_name == group_instance:
					self.relevant_groups.append(group_instance)
					break
		return self.relevant_groups

class DiscordObjectsGroup:
	"""
	Абстрактный класс объектов, реализующих доступ к данным через Discord API.
	"""

	USER_IDENTIFICATOR: str = ""

	def __init__(self, ctx: commands.Context) -> None:
		self.ctx = ctx

	def __eq__(self, right_operand: Any) -> bool:
		return self.USER_IDENTIFICATOR == right_operand

	def extractData(
		self,
		d_id: Optional[str] = None
	) -> Sequence[DiscordGuildObjects]:
		raise NotImplementedError

class UserGroup(DiscordObjectsGroup):
	"""
	Класс реализует доступ к `discord.Member <https://discordpy.\
	readthedocs.io/en/stable/api.html?highlight=member#discord.Member>`_
	в контексте гильдии.
	"""

	USER_IDENTIFICATOR: str = "usr"

	def extractData(
		self,
		d_id: Optional[str] = None
	) -> Sequence[DiscordGuildObjects]:
		if self.ctx.guild:
			return self.ctx.guild.members
		return []

class ChannelGroup(DiscordObjectsGroup):
	"""
	Класс реализует доступ к `discord.abc.Channel \
	<https://discordpy.readthedocs.io/en/stable/api.\
	html?highlight=guildchannel#discord.abc.GuildChannel>`_ в контексте
	гильдии.
	"""

	USER_IDENTIFICATOR: str = "ch"

	def extractData(
		self,
		d_id: Optional[str] = None
	) -> Sequence[DiscordGuildObjects]:
		if self.ctx.guild:
			return self.ctx.guild.channels
		return []

class DBObjectsGroup:
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

	def extractData(self, coord: Optional[str] = None) -> Iterable[str]:
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
		attrs: TargetGroupAttrs
	) -> None:
		self.dbconn = attrs["dbconn"]
		self.context_id = attrs["context_id"]
		self.dbrecord_id = attrs["dbrecord_id"] or self.generateID()
		self.target = attrs["target"]
		self.act = attrs["act"]
		self.d_in = attrs["d_in"]
		self.name = attrs["name"]
		self.output = attrs["output"]
		self.priority = attrs["priority"]
		self.other = attrs["other"]

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
					try:
						checking_nvalue = nvalue.replace(" ", "")
					except AttributeError:
						pass
					else:
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
					INSERT INTO target VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
					[self.dbrecord_id, self.context_id, self.target, self.act, self.d_in,
					self.name, self.output, self.priority, self.other])

	async def extractData(
		self,
		placeholder: Optional[str] = "*",
		**object_parameters: Any
	) -> List['TargetGroup']:
		r"""
		Args:
			\**object_parameters: параметры, которые будут переданы в SQL запрос. Если\
			параметров несколько, то они объединяются через логический оператора OR.
		"""
		values_for_parameters: List[Any] = []
		query = [psycopg.sql.SQL(
			f"SELECT {placeholder} FROM target WHERE context_id = %s")]
		values_for_parameters.append(self.context_id)
		if object_parameters:
			parameters_query_part: List[str] = []
			for (parameter, value) in object_parameters.items():
				parameters_query_part.append(f"{parameter} = %s")
				values_for_parameters.append(value)
			query.append(psycopg.sql.SQL(
				f"AND ({(' OR ').join(parameters_query_part)})"))

		async with self.dbconn.cursor() as acur:
			await acur.execute(
				psycopg.sql.SQL(" ").join(query) + psycopg.sql.SQL(";"),
				values_for_parameters
			)
			result: List[TargetGroup] = []
			for row in await acur.fetchall():
				dbrecord_id, context_id, target, act, d_in, name, priority, output, \
				other = row[0], row[1], row[2], row[3], row[4], row[5], row[6], \
				row[7], row[8]
				result.append(TargetGroup(TargetGroupAttrs(self.dbconn, context_id, target,
					act, d_in, name, priority, output, other, dbrecord_id)))
		return result

	def getComparableAttrs(self) -> Union[List[Any], None]:
		"""
		Формирует сравниваемые атрибуты.

		Returns:
			List[Any]: список атрибутов, которые имеет смысл сравнивать с другими\
			экземплярами :class:`TargetGroup`.
		"""
		if self.target and self.d_in:
			comparable_attrs: List[Any] = []
			objects_id: List[Any] = []
			for discord_objects in (self.target + self.d_in):
				objects_id.append(str(discord_objects.id))
			comparable_attrs += objects_id
			comparable_attrs.insert(len(self.target), self.act)
			comparable_attrs.append(self.name)
			return comparable_attrs
		return None

	def getCoincidenceTo(self, target: 'TargetGroup') -> str:
		"""
		Сравнить атрибуты с другим экземпляром :class:`TargetGroup`
		и вычислить точные совпадения.

		Returns:
			str: все совпавшие значения, перечисленных через запятую.
		"""
		if ((maybe_current_attr := self.getComparableAttrs()) and
			(maybe_compared_attr := target.getComparableAttrs())):
			current_attr: List[Any] = maybe_current_attr
			compared_attr: List[Any] = maybe_compared_attr
		coincidence_attrs: List[Any] = []
		for current_attr in current_attr:
			if current_attr in compared_attr and current_attr is not None:
				# is not None — исключаем из проверки None-объекты,
				# которые появляются только при отсутствии указания флага
				# -name.
				coincidence_attrs.append(current_attr)
		return ", ".join(list(coincidence_attrs))
