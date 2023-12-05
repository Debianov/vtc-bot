from typing import Any, List, Protocol, Union

import psycopg

from bot._types import IDObjects


class TargetGroupAttrs:

	def __init__(
		self,
		dbconn: psycopg.AsyncConnection[Any],
		context_id: int,
		target: List[IDObjects],
		act: Union[IDObjects, str],
		d_in: List[IDObjects],
		name: Union[str, None] = None,
		output: Union[str, None] = None,
		priority: Union[int, None] = None,
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
		self.output = output
		self.priority = priority
		self.other = other

	def keys(self):
		return list(self.__dict__.keys())

	def __getitem__(self, item):
		return self.__dict__[item]
