import abc
import os
from typing import (
	Any,
	Dict,
	Iterable,
	List,
	Optional,
	Tuple,
	Type,
	TypeVar,
	Union,
	Callable
)

import discord
from discord.ext import commands

from bot.data import DiscordObjectsGroup


class ContextProvider:
	"""
	Класс-локатор для приёма и передачи контекста.
	"""

	def __init__(self) -> None:
		self.context: Optional[discord.Guild] = None

	def updateContext(self, context: discord.Guild | None) -> None:
		self.context = context

	def getContext(self) -> Optional[discord.Guild]:
		return self.context


class MockLocator:
	"""
	Класс для приёма и передачи мок-объектов в виде объектов Discord для dpytest.
	"""

	def __init__(
			self,
			guild: discord.Guild,
			channel: discord.abc.GuildChannel,
			members: List[discord.Member]
	) -> None:
		self.guild = guild
		self.channel = channel
		self.members = members


class DiscordObjEvaluator:
	"""
	Существование класса обусловлено непреодолимым желанием разработчика
	иметь в записях под декоратором parametrize (в тестах) человеческие извлечения
	атрибутов. С указанием там имён всё довольно сложно, поскольку это
	происходит на этапе инициализации кода, и имена интерпретатор тупо не видит.
	"""

	def __init__(self, mock_locator: MockLocator):
		"""
		Args:
			mock_locator (MockLocator): аргумент необходим для обработки строк, которые
			, по задумке, содержат вызовы атрибутов данного.
		"""
		self.mock_locator = mock_locator

	def getMockLocator(self) -> MockLocator:
		return self.mock_locator

	def extractIDAndGenerateObject(
			self,
			sequence: List[str],
	) -> Iterable[str]:
		if sequence == [""]:
			return sequence
		message_part: List[str] = []
		for (ind, string) in enumerate(sequence):
			discord_object = self.evalForMockLocator(string)
			sequence[ind] = discord_object
			message_part.append(str(discord_object.id))
		return message_part if message_part else sequence

	def extractObjects(
			self,
			calls_sequence: List[str],
			current_ctx: commands.Context
	) -> List[List[discord.abc.Messageable]]:
		result: List[List[discord.abc.Messageable]] = []
		for call in calls_sequence:
			discord_objects = self.evalForMockLocator(call)
			result.append(list(discord_objects))
		return result

	def evalForMockLocator(
			self,
			expression: str
	) -> Any:
		split_expr = expression.split(".")
		obj_name = split_expr[0]
		if not obj_name == "mockLocator":
			return None
		attr_part = split_expr[1:]
		(attributes, indices) = self.evalAttributePart(attr_part)
		intermediate_eval_result: Any = \
			(self.mock_locator.__dict__[attributes[0]][indices[0]]
			 if indices[0] is not None else
			 self.mock_locator.__dict__[attributes[0]])
		if len(attributes) > 1 and len(indices) > 1:
			for (attr, index) in zip(attributes[1:], indices[1:]):
				if index is not None:
					intermediate_eval_result = \
						getattr(intermediate_eval_result, attr)[index]
				else:
					intermediate_eval_result = getattr(
						intermediate_eval_result, attr)
		return (total_eval_result := intermediate_eval_result)  # noqa: F841

	def evalAttributePart(
			self,
			attrs: List[str]
	) -> Tuple[List[str], List[Union[int, None]]]:
		attributes: List[str] = []
		indices: List[Union[int, None]] = []
		for attr in attrs:
			(attribute, index) = self.extractIndex(attr)
			attributes.append(attribute)
			indices.append(index)
		return (attributes, indices)

	def extractIndex(self, attr: str) -> Tuple[str, Union[int, None]]:
		if (((left_bracket_ind := attr.find("[")) == -1) and
				((
						 right_bracket_ind := attr.find(
							 "]")) == -1)):  # noqa: F841
			return (attr, None)
		cycle_cursor = left_bracket_ind + 1
		index = ""
		while attr[cycle_cursor].isdigit():
			index += attr[cycle_cursor]
			cycle_cursor += 1
		attr_without_index_part = attr.removesuffix(f"[{index}]")
		return (attr_without_index_part, int(index))


def getEnvIfExist(*env_names: str) -> Union[List[str], None]:
	"""
	Функция предназначена для проверки переменных окружения и возврата их значени
	й.

	Возвращает результаты в том же порядке, в котором передавали имена переменных.
	"""
	saved_data: List[str] = []
	for env in env_names:
		if not (result := os.getenv(env)):
			return None
		else:
			saved_data.append(result)
	return saved_data


def removeNesting(instance: List[Any]) -> List[Any]:
	"""
		The function for removing nesting.
	"""
	for elem in instance:
		if isinstance(elem, list):
			tmp = elem
			instance.remove(tmp)
			instance.extend(tmp)
	return instance


def createDiscordObjectsGroupInstance(
		instance_list: List[Type[DiscordObjectsGroup]],
		discord_context: commands.Context
) -> List[DiscordObjectsGroup]:
	result: List[DiscordObjectsGroup] = []
	for instance in instance_list:
		result.append(instance(discord_context))
	return result


T = TypeVar("T")


class DelayedExpression:

	def __init__(self, expression: str):
		self.expression = expression
		self.eval_expression: Any = None

	def eval(self, fixtures: Any) -> Any:
		self._setGlobalVarsInLocals(locals(), fixtures)
		return eval(self.expression)

	def _setGlobalVarsInLocals(
			self,
			locals: Dict[str, Any],
			fixtures: Any
	) -> Dict[str, Any]:
		"""
		Func set a local variable in a func that called it.
		"""
		for (key, value) in fixtures.items():
			locals[key] = value
		return locals

	@staticmethod
	def isMine(check_instance: Any) -> bool:
		"""
		The load == implement for a purpose that isinstance for an
		instance check don't work due a python
		`features <https://bugs.python.org/issue7555>`.
		"""
		return (hasattr(check_instance, "expression") and
				hasattr(check_instance, "eval_expression"))


class Case:
	"""
	The class for storing and passing args to test funcs. Also implement
	special storage for an args that are `DelayedExpressions`.

	Access to class attributes is any call to `__getitem__`.
	"""

	def __init__(self, **kwargs: Any) -> None:
		self.all_elems = kwargs

	def keys(self) -> List[Any]:
		"""
		The load func for a map object implementation.
		"""
		return list(self.all_elems.keys())

	def __getitem__(self, param) -> Any:
		return self.all_elems[param]

	def __setitem__(self, param: str, value: Any) -> None:
		self.all_elems[param] = value

class DelayedExprsEvaluator:
	"""
	Class evals every `DelayedExpression` in given list.
	"""

	def __init__(
			self,
			delayed_exprs: List[DelayedExpression],
			global_vars: Dict[str, Any]
	) -> None:
		"""
		Args:
			global_vars (Dict[str, Any]): any vars, that can be used for
			an expression eval.
		"""
		self.global_vars = global_vars
		self.delayed_exprs = delayed_exprs
		self.undelayed_exprs: List[Any] = []

	def go(self) -> None:
		self._setGlobalVarsInLocals(locals())
		for delay_expr in self.delayed_exprs:
			self.undelayed_exprs.append(eval(delay_expr.expression))

	def getUndelayedExprs(self) -> List[Any]:
		return self.undelayed_exprs

	def _setGlobalVarsInLocals(self, locals: Dict[str, Any]):
		"""
		Func set a local variable in a func that called it. It needs an eval
		DelayedExpr because it func loads the built-in eval(), which needs context
		as a global_vars.
		"""
		for (key, value) in self.global_vars.items():
			locals[key] = value
		return locals

class DelayedExpressionSubstitutor:
	"""
	The class for substituting elements in nested storages on the
	`self.to_substitute`.
	"""
	def __init__(self,
				 target: Dict[str, Any],
				 fixtures: Any
				 ):
		self.target = target
		self.current_target = target
		self.last_storage = target
		self.fixtures = fixtures
		self.last_mutable_storage: Union[Dict[str, Any], Tuple[Any], None] \
			= None
		self.class_to_change = DelayedExpression
		self.item: Union[str, int] = ""
		self.immutable_storages_chain: List[Tuple[Any, Union[str, int]]] = \
			[]
		self.item_to_access_immutable_storage = None

	def go(self) -> None:
		if not isinstance(self.current_target, self.class_to_change):
			previous_storage = self.setLastStorage(self.current_target)
			if (isinstance(self.current_target, dict) or
					isinstance(self.current_target, list)):
				self.last_mutable_storage = self.current_target
				self.immutable_storages_chain.clear()
				if isinstance(self.current_target, dict):
					for key, value in self.current_target.items():
						self.current_target = value
						self.item = key
						self.go()
				else:
					for ind, value in enumerate(self.current_target):
						self.current_target = value
						self.item = ind
						self.go()
			elif isinstance(self.current_target, tuple):
				self.immutable_storages_chain.append((self.current_target, self.item))
				self.addItemForAccessImmutableStorage(previous_storage)
				for ind, value in enumerate(self.current_target):
					self.current_target = value
					self.item = ind
					self.go()
				self.immutable_storages_chain.pop() if (
					self.immutable_storages_chain) else False
			self.last_storage = previous_storage
		else:
			delayed_expr = self.current_target
			evaled_expr = delayed_expr.eval(self.fixtures)
			self.insert(evaled_expr)

	def setLastStorage(self, target: Any) -> Any:
		"""
			Set `self.last_storage` and return old attr value that is necessary to restore a `self.last_storage` attr after
			exiting from a next recursive layer.
		"""
		previous_storage = self.last_storage
		self.last_storage = target
		return previous_storage

	def addItemForAccessImmutableStorage(self, previous_storage: Any) -> None:
		"""
		A func writes `self.item` to `item_to_access_immutable_storage`.
		`self.item_to_access_immutable_storage` stores `self.item` to access immutable storage from last mutable storage.
		If `previous_storage` is immutable storage `self.item` it doesn't save in `self.item_to_access_immutable_storage`.

		The fact of the matter is if `item_to_access_immutable_storage` is sets from an item that describes a position
		access to immutable storage (tuple) from list/or tuple consequently we can use this attr for access to tuples.
		```
		{'key': ("test", "test2", ["test3", "test4", ("test5", object_to_update1, (object_to_update2, "test6"))])}
		A path to object_to_update1: item = 2 from first tuple => item = 2 from first list.
		```
		If `item_to_access_immutable_storage` is sets from an item that describes a position access to immutable storage
		from other immutable storage, it's not allowed.
		```
		{'key': ("test", "test2", ["test3", "test4", ("test5", object_to_update1, (object_to_update2, "test6"))])}
		A wrong path to object_to_update2: item = 2 from first tuple => item = 2 from first list => item = 2 from second
		tuple.
		A true path to object_to_update2: item = 2 from first tuple => item = 2 from first list because first list is last
		mutable storage.
		```
		"""
		if isinstance(previous_storage, dict) or isinstance(previous_storage, list):
			self.item_to_access_immutable_storage = self.item

	def insert(self, object_to_insert: Any):
		if isinstance(self.last_storage, tuple):
			self.last_storage = _insertInTuple(self.last_storage, object_to_insert, self.item)
			self.updateImmutableChain(self.last_storage, self.immutable_storages_chain)
			self.last_mutable_storage[self.item_to_access_immutable_storage] = self.immutable_storages_chain[0][0]
		else:
			mutable_storage = self.last_storage
			mutable_storage[self.item] = object_to_insert

	def updateImmutableChain(self, storage_to_update: Tuple[Any], immutable_storages_chain: List[Tuple[Any]]) -> None:
		"""
		An updateImmutableChain func updates the entire chain starting with zero elements.
		"""
		immutable_storages_chain.reverse()
		for ind in range(0, len(immutable_storages_chain)):
			item_to_next_storage = immutable_storages_chain[ind][1]
			if ind == 0:
				immutable_storages_chain[ind] = (storage_to_update, item_to_next_storage)
			else:
				current_storage = immutable_storages_chain[ind][0]
				previous_storage = immutable_storages_chain[ind - 1][0]
				item_to_current_storage = immutable_storages_chain[ind - 1][1]
				current_storage = _insertInTuple(current_storage, previous_storage, item_to_current_storage)
				immutable_storages_chain[ind] = (current_storage, item_to_next_storage)
		immutable_storages_chain.reverse()

	def getResults(self) -> Dict[str, Any]:
		return self.target

def _insertInTuple(old_tuple: Tuple[Any], element_to_insert: Any, ind_to_insert: int) -> Tuple[Any]:
	new_tuple: Tuple[Any] = tuple()
	if not isinstance(ind_to_insert, int):
		raise Exception
	for (ind, elem) in enumerate(old_tuple):
		if ind == ind_to_insert:
			new_tuple += (element_to_insert,)
		else:
			new_tuple += (elem,)
	if element_to_insert not in new_tuple:
		raise Exception
	return new_tuple


class ElemFormater:

	def __init__(self, func: Callable[[Any], str]):
		self.format = func

	def getElemWithFormat(self, arg: Any) -> str:
		return self.format(arg)

def getStrObject(arg: Any) -> str:
    return str(arg)

default_format = ElemFormater(getStrObject)

class PartMessage(metaclass=abc.ABCMeta):

	@abc.abstractmethod
	def joinInStringPartMessage(self) -> str:
		raise NotImplementedError

class StringPartMessage(PartMessage, str):

	def __init__(self, text: str):
		self.text = text

	def joinInStringPartMessage(self) -> str:
		return self.text

class ListPartMessage(PartMessage, list):

	def __init__(self, format: ElemFormater, *args) -> None:
		self.format = format
		self.message_part: List[str] = []
		super().__init__(args)

	def joinInStringPartMessage(self, separator: str = " ") -> str:
		if not self.message_part:
			self._formMessagePart()
		return separator.join(self.message_part)

	def _formMessagePart(self) -> None:
		for elem in self:
			self.message_part.append(self.format.getElemWithFormat(elem))

class DictPartMessage(PartMessage, dict):

	def __init__(self, format: ElemFormater, *args, **kwargs) -> None:
		self.format = format
		self.message_part: List[str] = []
		self.only_values: List[str] = []
		self.update(*args, **kwargs)

	def joinInStringPartMessage(self) -> str:
		if not self.message_part:
			for key, value in self.items():
				if value:
					self.message_part.append(key)
					self.message_part.append(self.format.getElemWithFormat(value))
		return " ".join(self.message_part)

	def getValueAsList(self) -> str:
		for _, value in self.items():
			if value:
				self.only_values.append(self.format.getElemWithFormat(value))
			else:
				self.only_values.append(None)
		return self.only_values