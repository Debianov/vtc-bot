from typing import Final

class Text:

	def __init__(self, text: str) -> None:
		self.text = text
		self.processText()
		self.checkText()

	def __repr__(self):
		return self.getText()

	def getText(self) -> str:
		return self.text

	def processText(self) -> None:
		pass

class ActText(Text):

	ADD_ACT: Final = "+"
	DELETE_ACT: Final = "-"
	CHANGE_ACT: Final = ">"

	def checkText(self):
		for act_element in [self.ADD_ACT, self.DELETE_ACT, self.CHANGE_ACT]:
			if act_element not in self.text:
				raise WrongActSignal
			else:
				break

class DummyText(Text):
	pass

class StrOrIntText(Text):

	def checkText(self) -> None:
		if not self.text.isprintable(): # TODO проверка на несовпадения с упоминаниями и другими типами.
			raise WrongTextTypeSignal

class IntText(Text):

	def checkText(self) -> None:
		if not self.text.isdigit():
			raise WrongTextTypeSignal

class MentionText(Text):
	
	LEFT_BRACKET: Final = "<"
	RIGHT_BRACKET: Final = ">"

	def checkText(self) -> None:
		if not self.text.startswith(self.INDICATOR):
			raise WrongTextTypeSignal
		if not self.text[1:].isdigit():
			raise WrongTextTypeSignal

	def processText(self) -> None:
		self.text = self.text.removeprefix(self.LEFT_BRACKET)
		self.text = self.text.removesuffix(self.RIGHT_BRACKET)

class ChannelMentionText(MentionText):

	INDICATOR: Final = "#"

class UserMentionText(MentionText):

	INDICATOR: Final = "@"

class WrongTextTypeSignal(Exception):
	pass

class WrongActSignal(Exception):
	pass