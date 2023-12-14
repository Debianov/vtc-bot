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
	Union
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
		self.expression = expression

	@staticmethod
	def isMine(check_instance: Any) -> bool:
		"""
		The load == implement for a purpose that isinstance for an instance check
		don't work due a python `features <https://bugs.python.org/issue7555>`.
		"""
		return hasattr(check_instance, "expression")


class Case:
	"""
	The class for storing and passing args to test funcs. Also implement
	special storage for a args that are `DelayedExpressions`.

	Access to class attributes is any call to `__getitem__`.
	"""

	def __init__(self, **kwargs: Any) -> None:
		self.params_with_exprs_to_eval: Dict[str, List[DelayedExpression]] \
			= {}
		self.params_with_values: Dict[
			str, Optional[DelayedExpression]] = {}
		for key, value in kwargs.items():
			self._separateEvalExprsFromValues(kwargs[key], value)
			# if DelayedExpression.isMine(value):
			# 	self.params_with_exprs_to_eval[key] = [value]
			# elif isinstance(value, list) or isinstance(value, dict):
			# 	self._separateExprsToEvalFromValues(key, value)
			# 	delayed_exprs_from_param = (
			# 		self._extractDelayedExprsFromParamValue(value))
			# 	self.params_with_exprs_to_eval[key] = (
			# 		delayed_exprs_from_param)
			# 	self.params_with_values[key] = value
			# else:
			# 	self.simple_params[key] = value

	def _separateEvalExprsFromValues(
			self,
			storage: Union[Dict[Any, Any], List[Any]],
			value: Any
	) -> None:
		if isinstance(value, List):
			for value in value:
				self._separateEvalExprsFromValues(storage, value)
		elif isinstance(value, Dict):
			for key, value in value:
				self._separateEvalExprsFromValues(storage[key], value)
		elif isinstance(value, DelayedExpression):
			storage[key] = value
		else:
			storage[key] = value
		# 		if DelayedExpression.isMine(value):
		# 			self.params_with_exprs_to_eval[key] = (
		# 				self.params_with_exprs_to_eval[key].append(value)
		# 			)
		# 		else:
		# 			self.params_with_values[key] = (
		# 				self.params_with_values[key].append(value))
		# if isinstance(complex_value, dict):
		# 	self.params_with_exprs_to_eval[key] = {}
		# 	self.params_with_values[key] = {}
		# 	for complex_key, value in complex_value:
		# 		if DelayedExpression.isMine(value):
		# 			self.params_with_exprs_to_eval[key] = (
		# 				self.params_with_exprs_to_eval[key].update(
		# 					{complex_key: value}
		# 				)
		# 			)
		# 		else:
		# 			self.params_with_values[key] = (
		# 				self.params_with_values[key].append(value))

	def _isParamContainDelayedExprsAndValues(self, value: Any) -> bool:
		"""
		Check value for containing of at least one `DelayedExpression` and
		other values (it that is don't delay, i.e any objects except
		`DelayedExpression`).
		"""
		result = False
		for elem in value:
			if isinstance(elem, DelayedExpression):
				result = True
			elif result is True:
				result = False
				break
		return result

	def _extractDelayedExprsFromParamValue(
			self,
			value: Iterable
	) -> List[DelayedExpression]:
		delayed_exprs = []
		for elem in value:
			if isinstance(elem, DelayedExpression):
				delayed_exprs.append(elem)
		return delayed_exprs

	def keys(self):
		"""
		The load func for a map object implementation.
		:return:
		"""
		return list(self.simple_params.keys())

	def __getitem__(self, param) -> Any:
		return self.simple_params[param]

	def __setitem__(self, param: str, value: Any) -> None:
		self.simple_params[param] = value

	def getDelayedExprs(self) -> Dict[str, List[DelayedExpression]]:
		return self.params_with_exprs_to_eval

	def setUndelayedExprs(self, undelayed_exprs: Dict[str, Any]) -> None:
		"""
		Args:
			undelayed_exprs Dict[str, Any]: any params with a undelayed
			(evaled) expressions.
		"""
		for param, undelayed_expr in undelayed_exprs.items():
			new_value: Any = None
			if param in list(self.params_with_values.keys()):
				mixed_value = self.params_with_values[param]
				new_value = self._merge(undelayed_expr, mixed_value)
				self.params_with_values.pop(param)
			self.simple_params.update({param: new_value or undelayed_expr})
			self.params_with_exprs_to_eval.pop(param)

	@staticmethod
	def _merge(
			only_undelayed_exprs: Any,
			delayed_exprs_and_values: Any
	) -> Union[Dict[Any, Any], List[Any]]:
		"""
		Merge dict or list objects. Use to merge an undelayed expressions
		with other values as a comparison keys (in dict case) or index
		(in list case).

		Each argument must be of the same type.

		Returns:
			Union[Dict[Any, Any], List[Any]] - depending on the argument
			passed
		"""
		if isinstance(only_undelayed_exprs, dict) and isinstance(
				delayed_exprs_and_values, dict):
			result: Dict[Any, Any] = {}
			for key, value in only_undelayed_exprs():
				if (key in list(delayed_exprs_and_values.keys()) and
						DelayedExpression.isMine(
							delayed_exprs_and_values[key])):
					result[key] = value
				else:
					result[key] = delayed_exprs_and_values[key]
		elif isinstance(only_undelayed_exprs, list) and isinstance(delayed_exprs_and_values, list):
			result: List[Any] = []
			for (ind, value) in enumerate(only_undelayed_exprs):
				if DelayedExpression.isMine(delayed_exprs_and_values[ind]):
					result.append(value)
				else:
					result.append(delayed_exprs_and_values[ind])
		return result


class DelayedExpressionEvaluator:
	"""
	Class made with a `DelayedExpression` handle purpose.
	"""

	def __init__(
			self,
			delayed_expressions: List[DelayedExpression],
			global_vars: Dict[str, Any]
	) -> None:
		"""
		Args:
			global_vars (Dict[str, Any]): any vars, that can be used for
			an expression eval.
		"""
		self.delayed_expressions = delayed_expressions
		self.global_vars = global_vars

	def eval(self) -> List[Any]:
		self._setGlobalVarsInLocals(locals())
		result = []
		for delay_expression in self.delayed_expressions:
			result.append(eval(delay_expression.expression))
		return result

	def _setGlobalVarsInLocals(self, locals: Dict[str, Any]):
		for (key, value) in self.global_vars.items():
			locals[key] = value
		return locals
