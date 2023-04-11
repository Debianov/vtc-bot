from discord.ext import commands

class ErrorMessage:
	
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

class SearchExpressionNotFound(commands.BadArgument):

	def __init__(self, argument) -> None:
		self.argument = "Search Expression \"{}\" not found".format(argument)