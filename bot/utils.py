import os
from typing import Any, Iterable, List, Optional, Tuple, Union

import discord
from discord.ext import commands


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
		intermediate_eval_result: Any =\
			(self.mock_locator.__dict__[attributes[0]][indices[0]]
			if indices[0] is not None else
			self.mock_locator.__dict__[attributes[0]])
		if len(attributes) > 1 and len(indices) > 1:
			for (attr, index) in zip(attributes[1:], indices[1:]):
				if index is not None:
					intermediate_eval_result = getattr(intermediate_eval_result, attr)[index]
				else:
					intermediate_eval_result = getattr(intermediate_eval_result, attr)
		return (total_eval_result := intermediate_eval_result) # noqa: F841

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
			((right_bracket_ind := attr.find("]")) == -1)): # noqa: F841
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