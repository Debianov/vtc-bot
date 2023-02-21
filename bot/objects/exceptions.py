from typing import Tuple
from string import ascii_letters

class Error(Exception):
	
	def __init__(self, error_text: str) -> None:
		self.error_text = error_text

	def getText(self) -> str:
		return self.error_text

class UndefinedError(Error):
	
	def __init__(self) -> None:
		self.error_text = ("При выполнении операции произошла"
		" неопределённая/серверная ошибка.\nПожалуйста,"
		" повторите попытку позже. + \n\nЕсли ошибка повторяется,"
		" обратитесь в [тех. поддержку](//сайт тех. поддержки VCS//),"
		" предоставив системную информацию ниже.")

class ParameterError(Error):

	def __init__(self, parameter_name: str) -> None:
		self.parameter_name = parameter_name
		self.processParameterName()

	def getText(self) -> str:
		return self.error_text

	def processParameterName(self) -> None:
		if self.parameter_name.startswith("d_"):
			self.parameter_name = self.parameter_name.removeprefix("d_")

class DeterminingParameterError(ParameterError):
	
	def __init__(self, parameter_name: str) -> None:
		super().__init__(parameter_name) #? странная херня: как-то раз по
		# невнимательности оставил super без () — так никаких исключений даже не
		# возбудилось. Воспроизводил в отдельном файле данный класс и суперкласс
		# Error — всё возбуждается, хотя здесь нету никакх excep-шенов, которые всё
		# перехватывают. Чё за приколы?
		self.error_text = ("Убедитесь, что вы указали все обязательные аргументы"
		", либо указали параметры явно. Не найденные параметры: {}").\
		format(self.parameter_name) # TODO embedded

class ActParameterError(ParameterError):

	def __init__(self, parameter_name: str) -> None:
		super().__init__(parameter_name)
		self.text = "Убедитесь, что вы указали знак действия в параметре {}".\
		format(self.parameter_name) # TODO embedded

class UnmatchingParameterTypeError(ParameterError):

	def __init__(self, arg: str, arg_signature: Tuple[str, 'Text']):
		self.arg_signature = arg_signature
		self.arg = arg
		self.text = ""

	def getText(self) -> str:
		self.extractArgSignature()
		self.createErrorText()
		return self.text

	def extractArgSignature(self) -> None:
		self.parameter_name = self.arg_signature[0]
		self.parameter_type = self.arg_signature[1]

	def createErrorText(self) -> None:
		self.processErrorParameterType()
		self.text = ("Тип \"{}\" не соответствует значению \"{}\" в параметре"
		" \"{}\". Пожалуйста, исправьте значение.").format(self.parameter_type,
		self.arg, self.parameter_name)

	def processErrorParameterType(self) -> None:
		if self.parameter_type.userfriendly_name not in ascii_letters:
			self.parameter_type = self.parameter_type.userfriendly_name.lower()

class Signal(Exception):
	pass

class WrongTextTypeSignal(Signal):
	pass

class WrongActSignal(Signal):
	pass