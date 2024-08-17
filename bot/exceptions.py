"""
This module contains all exception classes.
"""
from __future__ import annotations

import abc
from typing import List, Tuple, TYPE_CHECKING

from discord.ext import commands

from bot._types import msgId

if TYPE_CHECKING:
	from bot.utils import Language

class ErrorMessage:
	"""
		This class implements a user error message that handles all
		exceptions.
	"""

	def __init__(self) -> None:
		self.text_start = ("Unexpected error occurs.\nPlease check:\n")
		self.current_point: int = 0

	def addError(self, error_text: str) -> None:
		self.current_point += 1
		self.__dict__[str(self.current_point)] = error_text

	def gatherError(self) -> str:
		text_rest: str = ""
		for i in range(1, self.current_point + 1):
			text_rest += "{}. ".format(str(i)) + self.__dict__[str(i)] + (
				"\n" if i != self.current_point else ...)
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


class StartupBotError(Exception):
	pass

class DuplicateInstanceError(Exception):
	"""
	If there are several identical instances, this error is raised.
	"""
	pass

class UserException(Exception, metaclass=abc.ABCMeta):

	@abc.abstractmethod
	def getUserDescriptionPattern(self) -> List[str]:
		raise NotImplementedError

	@abc.abstractmethod
	def getMsgId(self) -> str:
		raise NotImplementedError

class i18nException(Exception, metaclass=abc.ABCMeta):

	@abc.abstractmethod
	def __repr__(self):
		raise NotImplementedError


class AnyLangNameIsntDefined(i18nException):
	"""
	If any language name of `short_name` or `full_name` isn't defined, this
	exception will be thrown.
	"""

	def __repr__(self) -> str:
		return "No language is defined in the `Language` instance."


class UnsupportedLanguage(i18nException, UserException):
	"""
	If a language isn't supported by the bot, this error will be raised.
	"""

	def __init__(self, lang: Language) -> None:
		self.short_name = lang.getShortName() or lang.getFullName()

	def __repr__(self) -> str:
		return "the language isn't supported."

	def getUserDescriptionPattern(self) -> List[str]:
		return [self.short_name, ": ", "place_for_translated"]

	def getMsgId(self) -> str:
		return "language_isnt_supported"
