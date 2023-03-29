from typing import Final, List

from .exceptions import WrongActSignal, WrongTextTypeSignal
from ..utils import isDigitWithSpace, getBracketNotationStatus

class Text:

	userfriendly_name: str = "Системный тип"

	constants: List[str] = []

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
		string_with_digit = isDigitWithSpace(self.text, self.constants)
		self.constants.clear()
		if not string_with_digit:
			raise WrongTextTypeSignal

class MentionText(Text):
	
	LEFT_BRACKET: Final = "<"
	RIGHT_BRACKET: Final = ">"

	CHANNEL_MENTION_INDICATOR: Final = "#"
	USER_MENTION_INDICATOR: Final = "@"

	def checkText(self) -> None:
		if not self.text.startswith(self.LEFT_BRACKET):
			raise WrongTextTypeSignal()
		if not getBracketNotationStatus(self.text, self.LEFT_BRACKET, self.RIGHT_BRACKET):
			raise WrongTextTypeSignal()
		self.constants.extend([self.LEFT_BRACKET, self.RIGHT_BRACKET, self.CHANNEL_MENTION_INDICATOR, self.USER_MENTION_INDICATOR])
		# TODO добить список, чтобы его не переёбывало.
		text_instance = IntText(self.text)
		text_instance.checkText()

	def processText(self) -> None:
		super().processText()
		self.processed_text = self.processed_text.replace(self.LEFT_BRACKET, "")
		self.processed_text = self.processed_text.replace(self.RIGHT_BRACKET, "")

class ChannelMentionText(MentionText):

	userfriendly_name: str = "Упоминание канала"

	def checkText(self) -> None:
		self.constants.append(self.CHANNEL_MENTION_INDICATOR)
		super().checkText()
		if not self.text[1:].startswith(self.CHANNEL_MENTION_INDICATOR):
			raise WrongTextTypeSignal

class UserMentionText(MentionText):

	userfriendly_name: str = "Упоминание пользователя"

	def checkText(self) -> None:
		self.constants.append(self.USER_MENTION_INDICATOR)
		super().checkText()
		if not self.text[1:].startswith(self.USER_MENTION_INDICATOR):
			raise WrongTextTypeSignal