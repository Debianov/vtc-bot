"""
The module contains classes for working with databases.
"""
from __future__ import annotations
import abc
from typing import (
	Any,
	Dict,
	Iterable,
	List,
	Optional,
	Self,
	Sequence,
	Tuple,
	Type,
	Union,
	TYPE_CHECKING
)

import psycopg
from discord.ext import commands

from ._types import DiscordGuildObjects
from .attrs import TargetGroupAttrs

if TYPE_CHECKING:
	from .utils import Language

sql = psycopg.sql.SQL

class DataGroupAnalyzator:
	"""
	The class implements the mechanism for detecting
	the :class:`DiscordObjectsGroup` instance by name.
	"""

	def __init__(self, ctx: commands.Context, string: str) -> None:
		self.split_string: List[str] = string.split("+")
		self.relevant_groups: List[DiscordObjectsGroup] = []
		self.ctx = ctx

	def analyze(self) -> List['DiscordObjectsGroup']:
		"""
		The main method for detecting the :class:`DiscordObjectsGroup`
		instance.
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
	The abstract class implements access to data via Discord API.
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
	The class implements access to `discord.Member <https://discordpy.\
	readthedocs.io/en/stable/api.html?highlight=member#discord.Member>`_ in
	the context of a guild.
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
	The class implements access to `discord.abc.Channel \
	<https://discordpy.readthedocs.io/en/stable/api.\
	html?highlight=guildchannel#discord.abc.GuildChannel>`_ in
	the context of a guild.
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
	The abstract class implements accessing and writing data to the database.
	"""
	pass

class ActGroup(DBObjectsGroup):
	"""
	The class implements an object of user actions.
	"""
	def extractData(self, coord: Optional[str] = None) -> Iterable[str]:
		if not coord:
			pass
		return [""]

class TargetGroup(DBObjectsGroup):
	"""
	The class implements an object of the logging target.
	"""

	def __init__(
		self,
		attrs: TargetGroupAttrs
	) -> None:
		self.dbconn = attrs["dbconn"]
		self.context_id = attrs["context_id"]
		self.dbrecord_id = attrs["dbrecord_id"]
		self.target = attrs["target"]
		self.act = attrs["act"]
		self.d_in = attrs["d_in"]
		self.name = attrs["name"]
		self.output = attrs["output"]
		self.priority = attrs["priority"]
		self.other = attrs["other"]

	def _generateID(self) -> int:
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
				INSERT INTO target(context_id, target, act, d_in, name,
				priority, output, other)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
				[self.context_id, self.target, self.act, self.d_in,
				self.name, self.priority, self.output, self.other])

	async def extractData(
		self,
		placeholder: Optional[str] = "*",
		**object_parameters: Any
	) -> List['TargetGroup']:
		r"""
		Args:
			\**object_parameters: the parameters that will be passed in the
			SQL query. If the parameters is several then they will be
			concatenated through "OR" logical operator.
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

	def _getComparableAttrs(self) -> Union[List[Any]]:
		"""
		Forms comparable attributes.

		Returns:
			List[Any]: the attributes list that make sense for comparison
			with other instances of :class:`TargetGroup`.
		"""
		comparable_attrs: List[Any] = []
		if self.target and self.d_in:
			objects_id: List[Any] = []
			for discord_objects in (self.target + self.d_in):
				objects_id.append(str(discord_objects.id))
			comparable_attrs += objects_id
			comparable_attrs.insert(len(self.target), self.act)
			comparable_attrs.append(self.name)
		return comparable_attrs

	def getCoincidenceTo(self, target: 'TargetGroup') -> str:
		"""
		Compares attributes of the current instance with others of
		the :class:`TargetGroup` instance.

		Returns:
			str: all matching values separated by commas.
		"""
		current_attrs: List[Any] = self._getComparableAttrs()
		compared_attrs: List[Any] = target._getComparableAttrs()
		coincidence_attrs: List[Any] = []
		for current_attr in current_attrs:
			if current_attr in compared_attrs and current_attr is not None:
				coincidence_attrs.append(current_attr)
		return ", ".join(list(coincidence_attrs))


# class DBObjectsGroup(metaclass=abc.ABCMeta):
#
	#
	# @property
	# def _written(self) -> bool:
	# 	raise NotImplementedError
	#
	# def isWritten(self):
	# 	return self._written
	#
	# def _writtenNow(self):
	# 	self._written = True
	#
# 	@property
# 	def TABLE_NAME(self) -> str:
# 		raise NotImplementedError
#
#
# 	@property
# 	def DB_RECORD_FIELDS(self) -> List[str]:
# 		raise NotImplementedError
#
# 	@property
# 	def record_id(self) -> int:
# 		"""
# 		-1 if instance isn't written.
# 		"""
# 		raise NotImplementedError
#
# 	@property
# 	def change_map(self) -> Dict[str, bool]:
# 		raise NotImplementedError
#
# 	@abc.abstractmethod
# 	def __setattr__(self, key: str, value: Any) -> None:
# 		super().__setattr__(key, value)
#
# 	def __iter__():
# 		self._writtenNow()


class GuildDescription(DBObjectsGroup):

	TABLE_NAME: str = "guilds"
	DB_RECORD_FIELDS: List[str] = ['record_id', 'guild_id', 'selected_language']

	def __init__(
		self,
		record_id: int,
		guild_id: int,
		selected_language: Language
	) -> None:
		self._written = False
		self._change_map: Dict[str, bool] = {}
		self.record_id: int = record_id
		self.guild_id: int = guild_id
		self.selected_language: Language = selected_language

	def isWritten(self):
		return self._written

	def __setattr__(self, key: str, value: Any) -> None:
		if key in self.DB_RECORD_FIELDS:
			self._change_map.update({key: True})
		super().__setattr__(key, value)

	def __iter__(self) -> Self:
		self.field_cursor = 0
		return self

	def __next__(self) -> Tuple[bool, Tuple[str, Any]]:
		"""
		Returns:
			change_flag - `True` if an attr has been changed after instance
			init.
			field - of the DB record.
			value - of the field.
		"""
		if self.field_cursor > len(self.DB_RECORD_FIELDS) - 1:
			self._written = True
			raise StopIteration
		field = self.DB_RECORD_FIELDS[self.field_cursor]
		self.field_cursor += 1
		value = getattr(self, field)
		if flag := self._change_map.get(field):
			return flag, (field, value)
		else:
			return False, (field, value)

class DBObjectsGroupFabrics(metaclass=abc.ABCMeta):
	"""
	The class used to create a `DBObjectsGroup` instance, that isn't written
	in DB now.
	"""
	pass

class GuildDescriptionFabric(DBObjectsGroupFabrics):

	def __init__(
		self,
		guild_id: int,
		lang_instance: 'Language'
	) -> None:
		self.instance = GuildDescription(-1, guild_id, lang_instance)

	def getInstance(self) -> GuildDescription:
		return self.instance


async def updateDBRecord(
	dbconn: psycopg.AsyncConnection[Any],
	instance: DBObjectsGroup
) -> None:
	head_part: str = f"UPDATE {instance.TABLE_NAME}"
	mid_part: List[str] = ["SET"]
	end_part: str = "WHERE record_id = "
	parameters: List[Any] = []
	for attr_was_changed_flag, (attr, value) in instance:
		if attr == "record_id":
			end_part += value
		elif attr_was_changed_flag:
			mid_part.append(f"{attr} = %s")
			parameters.append(value)
	query = (head_part + "\n" + mid_part[0] + " " + ", ".join(mid_part[1:]) +
		"\n" + end_part + ";")
	async with dbconn.cursor() as acur:
		await acur.execute(sql(query), parameters)

async def findFromDB(
	dbconn: psycopg.AsyncConnection[Any],
	db_object_class: Type[DBObjectsGroup],
	**kwargs
) -> List[Union[DBObjectsGroup, None]]:
	result: List[db_object_class] = []
	table_name: str = db_object_class.TABLE_NAME
	head_query: str = f"SELECT * FROM {table_name}"
	condition_query: List[str] = ["WHERE"]
	for key, value in kwargs.items():
		condition_query.append(f"{key} = {value}")
	async with dbconn.cursor() as acur:
		await acur.execute(sql("\n".join([head_query,
		" ".join(condition_query)]) + ";"))
		for row in await acur.fetchall():
			result.append(db_object_class(*row))
	return result

async def createDBRecord(
	dbconn: psycopg.AsyncConnection[Any],
	instance: DBObjectsGroup
) -> None:
	head_part: str = f"INSERT INTO {instance.TABLE_NAME}"
	columns_part: List[str] = []
	values_part: List[str] = []
	parameters: List[Any] = []
	for _, (attr, value) in instance:
		if attr == "record_id":
			continue
		else:
			columns_part.append(attr)
			values_part.append("%s")
			parameters.append(value)
	query = (head_part + "(" + ", ".join(columns_part) + ")" + "\n" +
		"VALUES " + "(" + ", ".join(values_part) + ")" + ";")
	async with dbconn.cursor() as acur:
		await acur.execute(sql(query), parameters)