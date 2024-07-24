from abc import ABCMeta
from typing import Any, List, Union

import psycopg

from bot._types import IDObjects


class Attrs(metaclass=ABCMeta):

	def keys(self):
		return list(self.__dict__.keys())

	def __getitem__(self, item):
		return self.__dict__[item]

class TargetGroupAttrs(Attrs):

	def __init__(
		self,
		dbconn: psycopg.AsyncConnection[Any],
		context_id: int,
		target: List[IDObjects],
		act: Union[IDObjects, str],
		d_in: List[IDObjects],
		name: Union[str, None] = None,
		priority: Union[int, None] = 0,
		output: Union[str, None] = None,
		other: Union[str, None] = None,
		dbrecord_id: Union[int, None] = None
	):
		self.dbconn = dbconn
		self.context_id = context_id
		self.dbrecord_id = dbrecord_id
		self.target = target
		self.act = act
		self.d_in = d_in
		self.name = name
		self.priority = priority
		self.output = output
		self.other = other

class GuildDescriptionAttrs(Attrs):

	def __init__(
		self,
		guild_id: int,
		selected_language: str
	):
		self.guild_id: int = guild_id
		self.selected_language: str = selected_language