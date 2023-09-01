import os
from typing import List, Optional, Union, Iterable, Tuple, Any

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
		message_part: List[str] = []
		for (ind, string) in enumerate(sequence):
			discord_object = self.eval(string)
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
			discord_objects = self.eval(call)
			result.append(list(discord_objects))
		return result

	def eval(
		self,
		expression: str
	) -> Any:
		split_expr = expression.split(".")
		obj_name = split_expr[0]
		maybe_attribute_part = self.evalAttributePart(split_expr[1])
		index: Union[int, None] = None
		if len(maybe_attribute_part) == 2:
			index = int(maybe_attribute_part[1]) # type: ignore [misc]
		attribute_part = maybe_attribute_part[0]
		if "mockLocator" == obj_name and index:
			return self.mock_locator.__dict__[attribute_part][index]
		return self.mock_locator.__dict__[attribute_part]

	def evalAttributePart(self, expression: str) -> Tuple[str, ...]:
		(new_expr, index) = self.extractIndex(expression)
		if new_expr and index:
			return (new_expr, index)
		return (expression,)

	def extractIndex(self, expression: str) -> Union[Tuple[str, ...], Tuple[None, ...]]:
		if (((left_bracket_ind := expression.find("[")) == -1)
			and ((right_bracket_ind := expression.find("]")) == -1)):
			return (None, None)
		index = ""
		cycle_cursor = left_bracket_ind + 1
		while expression[cycle_cursor].isdigit():
			index += expression[cycle_cursor]
			cycle_cursor += 1
		new_expr = expression[:left_bracket_ind]
		return (new_expr, index)

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