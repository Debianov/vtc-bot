from typing import Final

from .exceptions import WrongActSignal, WrongTextTypeSignal, UndefinedError

class Text:

	user_name: str = "Системный тип"

	def __init__(self, text: str) -> None:
		self.text = text

	def __repr__(self) -> str:
		return self.getText()

	def getText(self) -> str:
		self.checkText()
		return self.text

	def checkText(self) -> None:
		pass

class ActText(Text):

	ADD_ACT: Final = "+"
	DELETE_ACT: Final = "-"
	CHANGE_ACT: Final = ">"

	def checkText(self) -> None:
		for act_element in [self.ADD_ACT, self.DELETE_ACT, self.CHANGE_ACT]:
			if act_element not in self.text:
				raise WrongActSignal
			else:
				break

class DummyText(Text):
	
	def __init__(self, text: str) -> None:
		self.text = text

	def getText(self) -> str:
		return self.text

class StrOrIntText(Text):

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

	def checkText(self) -> None:
		if not self.text.isdigit():
			raise WrongTextTypeSignal

class MentionText(Text):
	
	LEFT_BRACKET: Final = "<"
	RIGHT_BRACKET: Final = ">"

	def checkText(self) -> None:
		if not (self.text.startswith(self.LEFT_BRACKET) and self.text.endswith(self.RIGHT_BRACKET)):
			raise WrongTextTypeSignal
		self.processText()
		if not self.text[1:].isdigit():
			raise WrongTextTypeSignal

	def processText(self) -> None:
		self.text = self.text.removeprefix(self.LEFT_BRACKET)
		self.text = self.text.removesuffix(self.RIGHT_BRACKET)

class ChannelMentionText(MentionText):

	INDICATOR: Final = "#"

	def checkText(self) -> None:
		super().checkText()
		if not self.text.startswith(self.INDICATOR):
			raise WrongTextTypeSignal

class UserMentionText(MentionText):

	INDICATOR: Final = "@"

	def checkText(self) -> None:
		super().checkText()
		if not self.text.startswith(self.INDICATOR):
			raise WrongTextTypeSignal