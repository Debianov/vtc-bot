class Error(Exception):
	
	def getErrorText(self) -> str:
		return self.error_text

class UndefinedError(Error):
	
	def __init__(self):
		self.error_text = ("При выполнении операции произошла неопределённая/серверная ошибка.\nПожалуйста, повторите попытку позже." +
		"\n\nЕсли ошибка повторяется, обратитесь в [тех. поддержку](//сайт тех. поддержки VCS//), предоставив системную информацию ниже.")

class ParameterError(Error):

	def __init__(self, error_parameter: str) -> None:
		self.error_parameter = error_parameter
		self.processParameterName()

	def getErrorText(self) -> str:
		return self.error_text

	def processParameterName(self) -> None:
		if self.error_parameter.startswith("d_"):
			self.error_parameter = self.error_parameter.removeprefix("d_")

class DeterminingParameterError(ParameterError):
	
	def __init__(self, error_parameter: str) -> None:
		super().__init__(error_parameter) # TODO странная херня: как-то раз по невнимательности оставил super без () — так никаких исключений даже не возбудилось.
		# Воспроизводил в отдельном файле данный класс и суперкласс Error — всё возбуждается, хотя здесь нету никакх excep-шенов, которые всё перехватывают. Чё
		# за приколы?
		self.error_text = ("Убедитесь, что вы указали все обязательные аргументы" +
		",либо указали параметры явно. Не найденные параметры: {}").\
		format(self.error_parameter) # TODO embedded

class ActParameterError(ParameterError):

	def __init__(self, error_parameter: str) -> None:
		super().__init__(error_parameter)
		self.error_text = "Убедитесь, что вы указали знак действия в параметре {}".\
		format(self.error_parameter) # TODO embedded

class Signal(Exception):
	pass

class WrongTextTypeSignal(Signal):
	pass

class WrongActSignal(Signal):
	pass