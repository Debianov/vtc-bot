import builtins
import os
from typing import (
	Any,
	Callable,
	Dict,
	Iterable,
	List,
	Optional,
	Tuple,
	Type,
	TypeVar,
	Union
)

import discord
import discord.abc
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
			(attribute, index) = self.parseIndex(attr)
			attributes.append(attribute)
			indices.append(index)
		return (attributes, indices)

	def parseIndex(self, attr: str) -> Tuple[str, Union[int, None]]:
		if (((left_bracket_ind := attr.find("[")) == -1) and
				((right_bracket_ind := attr.find("]")) == -1)):  # noqa: F841
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

class Case(dict):
	"""
	The class for storing and passing args to test funcs.

	Access to class attributes is any call to `__getitem__`.
	"""

	def __init__(self, **kwargs: Any) -> None:
		"""
		Args:
			**kwargs (dict[str, Any])
		"""
		self.message_string: List[str] = []
		self.update(**kwargs)

	def getMessageStringWith(
		self,
		cmd: str,
		format_func: Callable[[Any], Any] = lambda x: x
	) -> str:
		"""
		Return the string for use in user messages.

		Args:
			format_func(Callable[[Any], Any]: should check an object type and
			get any necessary attrs.
		"""
		self.message_string.append(cmd)
		for elem in self.values():
			match type(elem):
				case builtins.list:
					for inner_elem in elem:
						self._addInMessageStringList(format_func(inner_elem))
				case builtins.dict:
					for key, value in elem.items():
						if value is not None:
							self._addInMessageStringList(format_func(key))
							self._addInMessageStringList(format_func(value))
				case _:
					self._addInMessageStringList(elem)
		return " ".join(self.message_string)

	def _addInMessageStringList(self, elem: Any):
		"""
		Check that elems of a `Case` is evaluated by `DelayedExprsEvaluator`.
		"""
		match type(elem):
			case builtins.int:
				self.message_string.append(str(elem))
			case builtins.str:
				self.message_string.append(elem)
			case _:
				raise TypeError("elem isn't str or int. Message string formation isn't "
								"possible.")

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

class DelayedExpressionReplacer:
	"""
	The class for replacing elements in nested storages on the
	the element of `fixtures` argument (respectively).
	"""
	def __init__(
		self,
		target: Iterable,
		fixtures: Any
	):
		self.target = target
		self.current_target = target
		self.last_storage = target
		self.fixtures = fixtures
		self.last_mutable_storage: Union[Dict[str, Any], List[Any], None] \
			= None
		self.class_to_change = DelayedExpression
		self.item: Union[str, int] = ""
		self.immutable_storages_chain: List[Tuple[Any, ...]] = []
		self.item_to_access_immutable_storage: Union[str, int, None] = None

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
			Set `self.last_storage` and return old attr value that is
			necessary to restore a `self.last_storage` attr after
			exiting from a next recursive layer.
		"""
		previous_storage = self.last_storage
		self.last_storage = target
		return previous_storage

	def addItemForAccessImmutableStorage(self, previous_storage: Any) -> None:
		"""
		A func writes `self.item` to `item_to_access_immutable_storage`.
		`self.item_to_access_immutable_storage` stores `self.item` to access
		immutable storage from last mutable storage. If `previous_storage`
		is immutable storage `self.item` it doesn't save in
		`self.item_to_access_immutable_storage`.

		The fact of the matter is if `item_to_access_immutable_storage` is
		sets from an item that describes a position
		access to immutable storage (tuple) from list/or tuple consequently
		we can use this attr for access to tuples.
		```
		{'key': ("test", "test2", ["test3", "test4",
		("test5", object_to_update1, (object_to_update2, "test6"))])}
		A path to object_to_update1: item = 2 from first tuple => item =
		2 from first list.
		```
		If `item_to_access_immutable_storage` is sets from an item that
		describes a position access to immutable storage
		from other immutable storage, it's not allowed (we won't be able
		"to write" anything in an immutable storage).
		```
		{'key': ("test", "test2", ["test3", "test4", ("test5",
		object_to_update1, (object_to_update2, "test6"))])}
		A wrong path to object_to_update2: item = 2 from first tuple =>
		item = 2 from first list => item = 2 from second tuple.
		A true path to object_to_update2: item = 2 from first tuple =>
		item = 2 from first list because first list is last mutable storage.
		```
		"""
		if isinstance(previous_storage, dict) or isinstance(previous_storage, list):
			self.item_to_access_immutable_storage = self.item

	def insert(self, object_to_insert: Any):
		if isinstance(self.last_storage, tuple) and isinstance(self.item, int):
			self.last_storage = _insertInTuple(self.last_storage,
											object_to_insert, self.item)
			self.updateImmutableChain(self.last_storage,
									self.immutable_storages_chain)
			if ((isinstance(self.last_mutable_storage, dict) and
			isinstance(self.item_to_access_immutable_storage, str)) or
			(isinstance(self.last_mutable_storage, list) and
			isinstance(self.item_to_access_immutable_storage, int))):
				self.last_mutable_storage[self. # type: ignore
				item_to_access_immutable_storage] = (self.
				immutable_storages_chain[0][0])
			else:
				raise TypeError("Unexpected type at assignment.")
		else:
			mutable_storage = self.last_storage # type: ignore
			mutable_storage[self.item] = object_to_insert # type: ignore

	def updateImmutableChain(
		self,
		storage_to_update: Tuple[Any],
		immutable_storages_chain: List[Tuple[Any, ...]]
	) -> None:
		"""
		An updateImmutableChain func updates the entire chain starting with
		zero elements.
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
				current_storage = _insertInTuple(
					current_storage,
					previous_storage,
					item_to_current_storage
				)
				immutable_storages_chain[ind] = (current_storage, item_to_next_storage)
		immutable_storages_chain.reverse()

	def getResults(self) -> Iterable:
		return self.target

def _insertInTuple(
	old_tuple: Tuple[Any],
	element_to_insert: Any,
	ind_to_insert: int
) -> Tuple[Any]:
	new_tuple: Tuple[Any, ...] = tuple()
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

def isIterable(obj: Any) -> bool:
	try:
		iter(obj)
	except TypeError:
		return False
	else:
		return True

def getDiscordMemberID(obj: Any) -> Any:
	if hasattr(obj, "id"):
		return obj.id
	else:
		print("getDiscordMemberID", f"the id attr hasn't been found in {obj}. Skip.")
		return obj