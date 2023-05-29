"""
Модуль содержит все классы исключения.
"""

from discord.ext import commands

class ErrorMessage:
	"""
		Класс реализует пользовательское сообщение со всеми ошибками.
	"""
	
	def __init__(self) -> None:
		self.text_start = ("При выполнении операции произошла пользовательская ошибка.\n"
		"Пожалуйста, убедитесь в следующем:\n")
		self.current_point: int = 0

	def addError(self, error_text: str) -> None:
		self.current_point += 1
		self.__dict__[current_point] = error_text

	def gatherError(self) -> str:
		text_rest: str = ""
		for i in range(1, self.current_point + 1):
			text_rest += "{}. ".format(str(i)) + self.__dict__[str(i)] + ("\n" if i != self.current_point else ...)
		return self.text_start + text_rest


class ExpressionNotFound(commands.BadArgument):
	pass

class SearchExpressionNotFound(ExpressionNotFound):

	def __init__(self, argument: str) -> None:
		self.argument = "Search search expression \"{}\" not found".format(argument)

class ShortSearchExpressionNotFound(SearchExpressionNotFound):

	def __init__(self, argument: str) -> None:
		self.argument = "Short search expression \"{}\" not found".format(argument)

class SpecialExpressionNotFound(ExpressionNotFound):

	def __init__(self, argument: str) -> None:
		self.argument = "Special expression \"{}\" not found".format(argument)

class UnhandlePartMessageSignal(Exception):

	def __init__(self, argument: str) -> None:
		self.argument = f"message_part {argument} unhandle"

	def __str__(self) -> str:
		return self.argument