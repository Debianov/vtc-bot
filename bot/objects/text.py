from typing import Final

from .exceptions import WrongActSignal, WrongTextTypeSignal

class Text:

	userfriendly_name: str = "Системный тип"

	def __init__(self, text: str) -> None:
		self.text = text
		self.processed_text: str = ""

	def __repr__(self) -> str:
		return self.getText()

	def getText(self) -> str:
		return self.text

	def getProcessedText(self) -> str:
		return self.processed_text

	def checkText(self) -> None:
		pass

	def processText(self) -> None:
		self.processed_text = self.text

class ActText(Text):

	ADD_ACT: Final = "+"
	DELETE_ACT: Final = "-"
	CHANGE_ACT: Final = ">"

	userfriendly_name: str = "ID действия"

	def checkText(self) -> None:
		for act_element in [self.ADD_ACT, self.DELETE_ACT, self.CHANGE_ACT]:
			if act_element == self.text[0]:
				return
		raise WrongActSignal

class DummyText(Text):
	
	def __init__(self, text: str) -> None:
		self.text = text

class StrOrIntText(Text):

	userfriendly_name: str = "Строка, число"

	def checkText(self) -> None:
		if not self.text.isprintable():
			raise WrongTextTypeSignal
		try:
			MentionText(self.text).checkText()
		except WrongTextTypeSignal:
			pass
		else:
			raise WrongTextTypeSignal

class IntText(Text):

	userfriendly_name: str = "Число"

	def checkText(self) -> None:
		if not self.text.isdigit():
			raise WrongTextTypeSignal

class MentionText(Text):
	
	LEFT_BRACKET: Final = "<"
	RIGHT_BRACKET: Final = ">"

	def checkText(self) -> None:
		if not (self.text.startswith(self.LEFT_BRACKET) and
		self.text.endswith(self.RIGHT_BRACKET)):
			raise WrongTextTypeSignal
		text_instance = IntText(self.text[2:-1])
		text_instance.checkText()

	def processText(self) -> None:
		super().processText()
		self.processed_text = self.processed_text.removeprefix(self.LEFT_BRACKET)
		self.processed_text = self.processed_text.removesuffix(self.RIGHT_BRACKET)

class ChannelMentionText(MentionText):

	INDICATOR: Final = "#"

	userfriendly_name: str = "Упоминание канала"

	def checkText(self) -> None:
		super().checkText()
		if not self.text[1:].startswith(self.INDICATOR):
			raise WrongTextTypeSignal

class UserMentionText(MentionText):

	INDICATOR: Final = "@"

	userfriendly_name: str = "Упоминание пользователя"

	def checkText(self) -> None:
		super().checkText()
		if not self.text[1:].startswith(self.INDICATOR):
			raise WrongTextTypeSignal