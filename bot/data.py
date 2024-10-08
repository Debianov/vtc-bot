"""
The module contains classes for working with databases.
"""
from __future__ import annotations

import abc
from typing import (
	TYPE_CHECKING,
	Any,
	Dict,
	Iterable,
	List,
	Optional,
	Self,
	Sequence,
	Tuple,
	Type,
	Union
)

import psycopg
from discord.ext import commands

from ._types import DiscordGuildObjects, IDObjects, operator

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
		self.relevant_groups: List[DiscordObjectGroup] = []
		self.ctx = ctx

	def analyze(self) -> List[DiscordObjectGroup]:
		"""
		The main method for detecting the :class:`DiscordObjectsGroup`
		instance.
		"""
		to_check: List[Type[DiscordObjectGroup]] =\
			DiscordObjectGroup.__subclasses__()
		copy_string: List[str] = self.split_string
		for group_name in copy_string:
			for group_type in to_check:
				group_instance = group_type(self.ctx)
				if group_name == group_instance:
					self.relevant_groups.append(group_instance)
					break
		return self.relevant_groups

class DiscordObjectGroup(metaclass=abc.ABCMeta):
	"""
	The abstract class implements access to data via Discord API.
	"""

	USER_IDENTIFICATOR: str = ""

	def __init__(self, ctx: commands.Context) -> None:
		self.ctx = ctx

	def __eq__(self, right_operand: Any) -> bool:
		return self.USER_IDENTIFICATOR == right_operand

	@abc.abstractmethod
	def extractData(
		self,
		d_id: Optional[str] = None
	) -> Sequence[DiscordGuildObjects]:
		raise NotImplementedError

class DefaultObjectGroup(DiscordObjectGroup):

	def extractData(
		self,
		d_id: Optional[str] = None
	) -> Sequence[DiscordGuildObjects]:
		return []

class UserGroup(DiscordObjectGroup):
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

class ChannelGroup(DiscordObjectGroup):
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

class DBObjectGroup(metaclass=abc.ABCMeta):
	"""
	The abstract class implements the database structures.
	"""

	FACTORY: Type[DBObjectsGroupFactory]

	def __init__(self):
		"""
		Implement by calling object.__setattr__ to avoid
		the superclass __setattr__.
		"""
		raise NotImplementedError

	@property
	def TABLE_NAME(self) -> str:
		"""
		The table_name that's associated with the `DBObjectGroup` instance.
		"""
		try:
			return self._TABLE_NAME
		except AttributeError:
			return ""

	@TABLE_NAME.setter
	def TABLE_NAME(self, new_value: str) -> None:
		self._TABLE_NAME = new_value

	@property
	def DB_RECORD_FIELDS(self) -> List[str]:
		try:
			return self._DB_RECORD_FIELDS
		except AttributeError:
			return []

	@DB_RECORD_FIELDS.setter
	def DB_RECORD_FIELDS(self, new_value: List[str]) -> None:
		self._DB_RECORD_FIELDS = new_value

	@property
	def guild_id(self) -> int:
		try:
			return self._guild_id
		except AttributeError:
			return -1

	@guild_id.setter
	def guild_id(self, new_value: int) -> None:
		self._guild_id = new_value

	@property
	def _change_map(self) -> Dict[str, bool]:
		"""
		Used in `__next__`.

		:return: the dict that contains keys of attrs from
		the `DB_RECORD_FIELDS` that have been modified by another
		funcs. A value is always True.
		"""
		try:
			return self._internal_change_map
		except AttributeError:
			self._internal_change_map: Dict[str, bool] = {}
			return self._internal_change_map

	@_change_map.setter
	def _change_map(self, new_value: Dict[str, bool]) -> None:
		self._internal_change_map = new_value

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
			raise StopIteration
		field = self.DB_RECORD_FIELDS[self.field_cursor]
		self.field_cursor += 1
		value = getattr(self, field)
		if flag := self._change_map.get(field):
			return flag, (field, value)
		else:
			return False, (field, value)

	def __eq__(self, other: object) -> bool:
		if isinstance(other, DBObjectGroup):
			for _, (field, value) in other:
				if not getattr(self, field) == value:
					return False
			return True
		else:
			return False

class DBObjectsGroupFactory(metaclass=abc.ABCMeta):
	"""
	The class used to create a `DBObjectsGroup` instance, that isn't written
	in DB now.
	It isn't recommended to manually create an instance based on this superclass.
	Use `DBObjectsGroupFabrics`.
	"""

	instance: Any

	def getInstance(self) -> Any:
		return self.instance

class GuildDescriptionFactory(DBObjectsGroupFactory):

	def __init__(
		self,
		guild_id: int,
		lang_instance: Language
	) -> None:
		self.instance = GuildDescription(int(guild_id), lang_instance)

	def getInstance(self) -> GuildDescription:
		return self.instance

class GuildDescription(DBObjectGroup):

	TABLE_NAME: str = "guilds"
	DB_RECORD_FIELDS: List[str] = ['guild_id', 'selected_language']
	FACTORY = GuildDescriptionFactory

	def __init__(
		self,
		guild_id: int,
		selected_language: Language
	) -> None:
		object.__setattr__(self, "_change_map", {})
		object.__setattr__(self, "guild_id", guild_id)
		object.__setattr__(self, "selected_language", selected_language)

class LogTargetFactory(DBObjectsGroupFactory):

	def __init__(
		self,
		guild_id: int,
		target: List[IDObjects],
		act: str,
		d_in: List[IDObjects],
		name: Union[str, None] = None,
		priority: Union[int, None] = None,
		output: Union[str, None] = None,
		other: Union[str, None] = None
	) -> None:
		self.instance = LogTarget(int(guild_id), target, str(act), d_in,
		name, int(priority) if priority is not None else None, output, other)

	def getInstance(self) -> LogTarget:
		return self.instance

class LogTarget(DBObjectGroup):
	"""
	The class implements an object of the logging target.
	"""

	TABLE_NAME: str = "log_targets"
	DB_RECORD_FIELDS: List[str] = ['guild_id', 'target', 'act', 'd_in',
	'name', 'priority', 'output', 'other']
	FACTORY = LogTargetFactory

	def __init__(
		self,
		guild_id: int,
		target: List[IDObjects],
		act: str,
		d_in: List[IDObjects],
		name: Union[str, None],
		priority: Union[int, None],
		output: Union[str, None],
		other: Union[str, None]
	) -> None:
		object.__setattr__(self, "guild_id", guild_id)
		object.__setattr__(self, "target", target)
		object.__setattr__(self, "act", act)
		object.__setattr__(self, "d_in", d_in)
		object.__setattr__(self, "name", name)
		object.__setattr__(self, "priority", priority)
		object.__setattr__(self, "output", output)
		object.__setattr__(self, "other", other)

	def _getComparableAttrs(self) -> Union[List[Any]]:
		"""
		It forms comparable attributes.

		Returns:
			List[Any]: the attributes list that make sense for comparison
			with other instances of :class:`LogTarget`.
		"""
		comparable_attrs: List[Any] = []
		if self.target and self.d_in: # type: ignore[attr-defined]
			objects_id: List[Any] = []
			for discord_objects in (self.target + # type: ignore[attr-defined]
			self.d_in): # type: ignore[attr-defined]
				objects_id.append(str(discord_objects.id))
			comparable_attrs += objects_id
			comparable_attrs.insert(len(self.target), # type:ignore[attr-defined]
				self.act) # type: ignore[attr-defined]
			comparable_attrs.append(self.name) # type: ignore[attr-defined]
		return comparable_attrs

	def getCoincidenceTo(self, target: LogTarget) -> str:
		"""
		It compares attributes of the current instance with others of
		the :class:`LogTarget` instance.

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

class ActGroup:
	"""
	The class implements an object of user actions.
	"""
	def extractData(self, coord: Optional[str] = None) -> Iterable[str]:
		if not coord:
			pass
		return [""]


async def updateDBRecord(
	dbconn: psycopg.AsyncConnection[Any],
	instance: DBObjectGroup
) -> None:
	head_part: str = f"UPDATE {instance.TABLE_NAME}"
	mid_part: List[str] = ["SET"]
	end_part: str = "WHERE guild_id = "
	parameters: List[Any] = []
	for attr_was_changed_flag, (attr, value) in instance:
		if attr == "guild_id":
			end_part += str(value)
		elif attr_was_changed_flag:
			mid_part.append(f"{attr} = %s")
			parameters.append(value)
	query = (head_part + "\n" + mid_part[0] + " " + ", ".join(
		mid_part[1:]) + "\n" + end_part + ";")
	async with dbconn.cursor() as acur:
		await acur.execute(sql(query), parameters)

async def findFromDB(
	dbconn: psycopg.AsyncConnection[Any],
	db_object_class: Type[DBObjectGroup],
	operators_dict_map: Dict[str, operator] = {},
	**kwargs
) -> List[DBObjectGroup]:
	"""
	:param operators_dict_map: It specifies where logical operators `OR`/`AND`
	are located in the `SELECT WHERE` SQL statement.
	The key is an index range, the value is logical operator `_types.OR`/
	`_types.AND`.
	If an index is missing, `IndexError` is thrown.
	If the parameter isn't specified, `AND` operator is used by default.
	The parameter isn't needed if there is only one parameter in the kwargs.
	For example: {0: OR, 1-4: AND} — OR on index 0, AND on index 1 to 4.
	.. important:: indexes must be enums in ascending order.
	"""
	result: List[DBObjectGroup] = []
	factory = db_object_class.FACTORY
	table_name: str = db_object_class.TABLE_NAME # type: ignore[assignment]
	head_query: str = f"SELECT * FROM {table_name}"
	condition_query: List[str] = ["WHERE"]
	parameters: List[Any] = []
	if len(kwargs.items()) <= 1:
		for ind, (key, value) in enumerate(kwargs.items()):
			condition_query.append(f"{key} = %s")
			parameters.append(value)
	else:
		operators_map = _convertToListMap(operators_dict_map)
		for ind, (key, value) in enumerate(kwargs.items()):
			condition_query.append(f"{key} = %s")
			if not ind == len(kwargs.items()) - 1:
				condition_query.append(operators_map[ind])
			parameters.append(value)
	async with dbconn.cursor() as acur:
		await acur.execute(sql("\n".join([head_query,
		" ".join(condition_query)]) + ";"), parameters)
		for row in await acur.fetchall():
			result.append(factory(*row).getInstance())
	return result

def _convertToListMap(dict_map: Dict[str, operator]) -> List[operator]:
	result: List[operator] = []
	str_operators: List[str] = ["OR", "AND"]
	for key, value in dict_map.items():
		if "-" in key:
			start_range, end_range = key.split("-")
			for ind in range(int(start_range), int(end_range) + 1):
				if not (ind == len(result)):
					raise IndexError("missed index in the map")
				result.append(str_operators[value])
		else:
			if not (int(key) == len(result)):
				raise IndexError("missed index in the map")
			result.append(str_operators[value])
	return result

async def createDBRecord(
	dbconn: psycopg.AsyncConnection[Any],
	instance: DBObjectGroup
) -> None:
	head_part: str = f"INSERT INTO {instance.TABLE_NAME}"
	columns_part: List[str] = []
	values_part: List[str] = []
	parameters: List[Any] = []
	for _, (attr, value) in instance:
		columns_part.append(attr)
		values_part.append("%s")
		parameters.append(value)
	query = (head_part + "(" + ", ".join(columns_part) + ")" + "\n" +
				"VALUES " + "(" + ", ".join(values_part) + ")" + ";")
	async with dbconn.cursor() as acur:
		await acur.execute(sql(query), parameters)