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
	SupportsIndex
)

import discord
from discord.ext import commands

from _types import SupportItems
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


def removeNesting(instance: Any) -> Any:
	"""
		Функция для удаления вложенностей.

		Returns:
			Optional[List[discord.abc.Messageable]]
	"""
	if len(instance) == 1 and isinstance(instance[0], list):
		tmp = instance[0]
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
		self.eval_expression: Any = Any
		self.expression = expression

	def setEvaledResult(self, result: Any):
		self.eval_expression = result

	@staticmethod
	def isMine(check_instance: Any) -> bool:
		"""
		The load == implement for a purpose that isinstance for an instance check
		don't work due a python `features <https://bugs.python.org/issue7555>`.
		"""
		return hasattr(check_instance, "expression") and hasattr(check_instance, "eval_expression")


class Case:
	"""
	The class for storing and passing args to test funcs. Also implement
	special storage for an args that are `DelayedExpressions`.

	Access to class attributes is any call to `__getitem__`.
	"""

	def __init__(self, **kwargs: Any) -> None:
		self.all_params = kwargs
		self.storages_with_delayed_exprs: Dict[Any, Any] = {}
		self.findDelayedExprs(kwargs)

	def keys(self) -> List[Any]:
		"""
		The load func for a map object implementation.
		"""
		return list(self.all_params.keys())

	def __getitem__(self, param) -> Any:
		return self.all_params[param]

	def __setitem__(self, param: str, value: Any) -> None:
		self.all_params[param] = value

	def getDelayedExprs(self) -> List[DelayedExpression]:
		return list(self.storages_with_delayed_exprs.values())


class CaseEvaluator:
	"""
	Class made in order to process the `Case` that stores the
	`DelayedExpression`.
	"""

	def __init__(
			self,
			global_vars: Dict[str, Any],
			param: str,
			value: Any
	) -> None:
		"""
		Args:
			global_vars (Dict[str, Any]): any vars, that can be used for
			an expression eval.
		"""
		self.param = param
		self.value = value
		self.global_vars = global_vars

	def eval(self) -> List[Any]:
		self._setGlobalVarsInLocals(locals())
		searcher = NestedSearcher(self.value, DelayedExpression)
		searcher.go()
		for search_result in searcher.getResults():
			storage_stack = search_result.storage_stack
			current_storage: Union[List[Any], Dict[str, Any], Tuple[Any]] = \
				None
			stack_cursor = len(storage_stack) - 1
			while stack_cursor != 0:
				first_mutable_storage = storage_stack[stack_cursor]
				if (isinstance(first_mutable_storage, dict) or
					isinstance(first_mutable_storage, list)):
					mutable_storage = first_mutable_storage
					value = storage_stack[stack_cursor + 1]
					break
				else:
					stack_cursor -= 1
			# mutable_storage[item] = mutable_storage
		return result

	def _setGlobalVarsInLocals(self, locals: Dict[str, Any]):
		"""
		Func set a local variable in a func that called it. It needs an eval
		DelayedExpr because it func loads the built-in eval(), which needs context
		as a global_vars.
		"""
		for (key, value) in self.global_vars.items():
			locals[key] = value
		return locals

class NestedSearcher:

	def __init__(self,
			 current_obj: Dict[str, Any],
			 search_target: Any
		):
		self.maybe_target = current_obj
		self.search_target: Any = search_target
		self.value = None
		self.item: Union[str, int] = list(current_obj.keys())[0]
		self.storage_stack = []
		self.result: List[NestedSearcherResult] = []

	def go(self) -> None:
		if isinstance(self.maybe_target, dict):
			self.storage_stack.append((self.maybe_target, self.item))
			for key, value in self.maybe_target.items():
				self.maybe_target = value
				self.item = key
				self.go()
		elif isinstance(self.maybe_target, list):
			self.storage_stack.append((self.maybe_target, self.item))
			for ind, value in enumerate(self.maybe_target):
				self.maybe_target = value
				self.item = ind
				self.go()
		elif isinstance(self.maybe_target, tuple):
			self.storage_stack.append((self.maybe_target, self.item))
			for ind, value in enumerate(self.maybe_target):
				self.maybe_target = value
				self.item = ind
				self.go()
		elif isinstance(self.maybe_target, self.search_target):
			storage_stack_ind = -1
			storage: Union[Dict[Any, Any], Tuple[Any], List[Any]] = None
			item: Union[str, int] = None
			while storage_stack_ind != -len(self.storage_stack) - 1:
				storage, item = self.storage_stack[storage_stack_ind]
				if not isinstance(storage, tuple):
					break
				storage_stack_ind -= 1
			storage[item] = "ПЕРЕУЧЁТ"

	def getResults(self) -> List['NestedSearcherResult']:
		return self.result

class NestedSearcherResult:

	def __init__(
		self,
		storage_stack: List[Union[List[Any], Dict[str, Any], Tuple[Any]]],
		current_obj: Any,
		item: Union[int, str]
	):
		self.stack_storage = storage_stack
		self.current_obj = current_obj
		self.item = item

	def keys(self) -> List[str]:
		"""
		The load func for a map object implementation.
		"""
		return ["previous_obj", "current_obj", "item", "value"]

	def __getitem__(self, item) -> Any:
		return self.__dict__[item]