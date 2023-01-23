class Error(Exception):

	def __init__(self, error_parameter: str):
		self.error_parameter = error_parameter
		self.processParameterName()

	def getErrorText(self) -> str:
		return self.error_text

	def processParameterName(self) -> None:
		if self.error_parameter.startswith("d_"):
			self.error_parameter = self.error_parameter.removeprefix("d_")

class DeterminingParameterError(Error):
	
	def __init__(self, error_parameter: str) -> None:
		super.__init__(error_parameter)
		self.error_text = ("Убедитесь, что вы указали все обязательные аргументы,\
		либо указали параметры явно. Не найденные параметры: {}").\
		format(self.error_parameter) # TODO embedded

try:
	raise DeterminingParameterError("SADASD")
except:
	print("DASDAD!")
print("SASD!")