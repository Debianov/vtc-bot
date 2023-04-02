# 	# TODO надо что-то с ошибками types делать. Пока не критично.
from typing import Union, List, Dict, Tuple, Callable, Any, Optional, get_args,\
get_origin
from types import UnionType
import discord

from .commands import commands_collection, dummyCommand, Required
from bot.utils import getCallSignature, splitWithSpaceRemoving
from .text import Text
from .exceptions import DeterminingParameterError, ActParameterError,\
WrongTextTypeSignal, WrongActSignal, UnmatchingParameterTypeError

class UserAction:

	def __init__(self, d_id: int, author: discord.Member,
	start_time: int) -> None:
		self.d_id = d_id
		self.author = author
		self.start_time = start_time
		self.finish_time: str
		self.result: str

class UserMessage(UserAction):

	def __init__(self, d_id: int, author: discord.Member, start_time: int,
	guild: 'Guild', content: 'Content', channel: discord.TextChannel) -> None:
		super().__init__(d_id, author, start_time)
		self.guild = guild
		self.content = content
		self.channel = channel
		self.content.extractPrefixes()

	def isCommand(self) -> bool:
		if self.content.getGlobalPrefix():
			return True
		return False

	async def reply(self) -> None:
		self.content.extractCommand(commands_collection)
		self.content.extractParameters()
		method = self.content.getCommand()
		parameters = self.content.getParameters()
		await method(self.channel, **parameters)

	async def reply_by_custome_text(self, text: str) -> None:
		await self.channel.send(text)

	async def handle(self) -> None:
		pass

class Guild:

	def __init__(self, global_prefix: str, access_prefix: str) -> None:
		self.global_prefix = global_prefix
		self.access_prefix = access_prefix

	def getGlobalPrefix(self) -> str:
		return self.global_prefix

	def getAccessPrefix(self) -> str:
		return self.access_prefix

class Content:

	def __init__(self, text: str, current_global_prefix: str, current_access_prefix: str) -> None: # TODO
	# discord.Thread не могу вставить в Union: нету атрибута такого, хотя по
	# докам всё сходится.
		self.original_text = text
		self.current_global_prefix = current_global_prefix
		self.current_access_prefix = current_access_prefix
		self.func: Callable[..., None] = dummyCommand
		self.global_prefix: str = ""
		self.access_prefix: str = ""
		self.expect_parameters: Dict[str, Text] = {}
		self.original_parameters_text: str = ""

	def __str__(self) -> str:
		return self.original_text

	def createTextCopy(self) -> None:
		self.original_parameters_text = self.original_text

	def getGlobalPrefix(self) -> str:
		return self.global_prefix

	def getAccessPrefix(self) -> str:
		return self.access_prefix

	def getParameters(self) -> Dict[str, Text]:
		return self.processed_parameters

	def getCommand(self) -> Callable[[Any], None]:
		return self.func

	def extractPrefixes(self) -> None: # TODO проверить на пробелы.
		if not self.original_parameters_text:
			self.createTextCopy()
		self.extractGlobalPrefix()
		self.extractAccessPrefix()
		self.removeSpaceAfterPrefixes()

	def extractGlobalPrefix(self) -> None:
		if not self.global_prefix:
			if self.original_parameters_text.startswith(self.current_global_prefix):
				self.original_parameters_text = self.original_parameters_text.removeprefix(self.current_global_prefix)
				self.global_prefix = self.current_global_prefix

	def extractAccessPrefix(self) -> None:
		if not self.access_prefix:
			if self.original_parameters_text.startswith(self.current_access_prefix):
				self.original_parameters_text = self.original_parameters_text.removeprefix(self.current_access_prefix + " ")
				self.access_prefix = self.current_access_prefix

	def removeSpaceAfterPrefixes(self) -> None:
		self.original_parameters_text = self.original_parameters_text.removeprefix(" ")

	def extractCommand(self, name_extraction_object:
		Dict[str, Union[Callable[..., None], Dict[str,
		Callable[..., None]]]]) -> None:
		# TODO сделать особый тип str, где есть разделение |, которое используется в
		# распознавании алиасов одной и той же команды.
		# TODO и тут в name_extraction_object аннотация слишком большая. Не создать
		# ли нам generic?
		# TODO bug: при игнорировании подкоманды пользователем происходит ошибка.
		for extract_name in name_extraction_object:
			command_names = extract_name.split("|")
			for command_name in command_names:
				if self.original_parameters_text.startswith(command_name):
					self.original_parameters_text = self.original_parameters_text.removeprefix(command_name + " ")
					value = name_extraction_object[extract_name]
					if isinstance(value, dict):
						self.extractCommand(value)
					else:
						self.func = value
					break

	def extractParameters(self) -> None: # TODO обработка пар параметров.
		self.expect_parameters = all_parameters_current_command =\
		getCallSignature(self.func)
		self.processed_parameters: Dict[str, Text] = {}
		self.split_user_text = list(splitWithSpaceRemoving(self.original_parameters_text))
		while self.split_user_text:
			parameter_or_parameter_arg = self.split_user_text.pop(0)
			if parameter_or_parameter_arg.startswith("-"): # TODO баг: -object может
				# быть распознан как параметр.
				parameter = Parameter(parameter_or_parameter_arg, self.split_user_text, self.expect_parameters)
				parameter.process()
				related_arg = self.split_user_text.pop(0)
				args = Args(related_arg, self.split_user_text, self.expect_parameters, self.processed_parameters, parameter)
				args.process()
			else:
				args = Args(parameter_or_parameter_arg, self.split_user_text, self.expect_parameters, self.processed_parameters)
				args.process()
		self.checkForMissingRequiredParameters()
		self.extendParametersByOptionalParameters()

	def checkForMissingRequiredParameters(self) -> None:
		maybe_missing_required_parameters = self.expect_parameters
		for (parameter, parameter_types) in\
		maybe_missing_required_parameters.items():
			try: #? лучше, чем через isinstance?
				parameter_required_or_not = Required in parameter_types
			except TypeError:
				parameter_required_or_not = Required is parameter_types
			finally:
				if parameter_required_or_not:
					raise DeterminingParameterError(parameter)

	def extendParametersByOptionalParameters(self) -> None:
		current_command_signature = getCallSignature(self.func)
		for parameter in current_command_signature:
			if parameter not in self.processed_parameters:
				self.processed_parameters.update({parameter: ""})

class Args:
	
	def __init__(self, args: str, split_user_text: List[str], expect_parameters: Dict[str, Any], processed_parameters: Dict[str, Text], parameter_instance: Optional['Parameter'] = None) -> None:
		self.args: List[str] = [args] # TODO с точки зрения ООП этот args нужно засовывать в Text.
		# TODO даже можно со сплита начать.
		self.split_user_text = split_user_text
		self.expect_parameters = expect_parameters
		self.parameter_instance: Optional[Parameter] = parameter_instance
		self.processed_parameters = processed_parameters

	def process(self) -> None:
		self.extractArgsGroup()
		if self.parameter_instance:
			self.parameter_instance.process()
			self.processWithExplicitParameter()
		else:
			self.processWithImplicitParameter()

	def processWithExplicitParameter(self) -> None:
		parameter_without_prefix = self.parameter_instance.getNameParameterWithoutPrefix()
		converted_args = self.convertedArg()
		if converted_args:
			self.processed_parameters[parameter_without_prefix] = converted_args # TODO вместо parameter_without_prefix как вариант юзать parameter_instance
			self.expect_parameters.pop(parameter_without_prefix) # TODO converted_args на вывод, а добавление в found и expect_parameters сделат в extractParameters.
		else:
			raise UnmatchingParameterTypeError(*self.getSignature()) # TODO вывод типов, которые, возможно, имелись ввиду, организовать.

	def processWithImplicitParameter(self) -> None:
		for (parameter, parameter_types) in self.expect_parameters.items():
			self.parameter_instance = Parameter(parameter, self.split_user_text, self.expect_parameters)
			self.parameter_instance.process()
			converted_args = self.convertedArg()
			if converted_args: # TODO нейминги.
				self.processed_parameters[parameter] = converted_args
				self.expect_parameters.pop(parameter)
				break
		else:
			raise UnmatchingParameterTypeError(*self.getSignature()) # TODO вывод типов, которые, возможно, имелись ввиду, организовать.

	def extractArgsGroup(self) -> None:
		if self.isArgsGroup():
			self.args[0] = self.args[0].removeprefix("\"")
			while True:
				self.args.append(self.split_user_text.pop(0))
				if self.args[-1].endswith("\"") or self.args[0].endswith("\""): # TODO bag zone + сделать ошибку для группы аргументов
					break
			self.args[-1] = self.args[-1].removesuffix("\"")

	def isArgsGroup(self) -> bool:
		if self.args[0].startswith("\""): # TODO метод проверки нужно будет поменять (ну или подумать над ним хотя б).
			return True
		return False

	def convertedArg(self) -> str:
		check_types: List[Text] = []
		processed_arg_text: str = ""
		self.generateCheckTypes(self.parameter_instance.getExpectTypes(), check_types)
		for check_type in check_types:
			try:
				check_parameter_type_instance = check_type(" ".join(self.args))
				check_parameter_type_instance.checkText()
				check_parameter_type_instance.processText()
				processed_arg_text = check_parameter_type_instance.getProcessedText()
				break
			except WrongTextTypeSignal:
				pass
			except WrongActSignal:
				raise ActParameterError(self.parameter_instance.getNameParameterWithoutPrefix())
		return processed_arg_text

	def generateCheckTypes(self, parameter_types: Union[Text, Tuple[Required,
	Text]], check_types: List[Text]) -> None:
		if isinstance(parameter_types, tuple):
			for parameter_type in parameter_types:
				if self.isUnionType(parameter_type):
					check_types.extend(self.extractUnionType(parameter_type))
				elif issubclass(parameter_type, Text):
					check_types.append(parameter_type)
		else:
			check_types.append(parameter_types)

	def isUnionType(self, parameter_type: Union[UnionType, Text, Required])\
	-> bool: # TODO это вообще в Азейрбаджан отправить желательно вместе с методом ниже.
		if get_origin(parameter_type) is Union:
			return True
		return False

	def extractUnionType(self, parameter_type: Union) -> List[Text]:
		union_args = get_args(parameter_type)
		result: List[Text] = []
		for parameter_type in union_args:
			result.append(parameter_type)
		return result

	def getSignature(self) -> Tuple[str, str, Text]:
		return (self.args, self.parameter_instance.getNameParameterWithoutPrefix(), self.parameter_instance.getExpectTypes())

class Parameter:

	def __init__(self, parameter: str, split_user_text: List[str], expect_parameters: Dict[str, Any]) -> None:
		self.parameter = parameter
		self.split_user_text = split_user_text
		self.expect_parameters = expect_parameters
		self.parameter_types: Union[Text, Tuple[Required, Text]] = None

	def __repr__(self) -> str:
		return self.parameter

	def process(self) -> None:
		self.parameter_without_prefix = self.parameter.removeprefix("-")
		if self.parameter_without_prefix in self.expect_parameters:
			self.parameter_types = self.expect_parameters[self.parameter_without_prefix]

	def getNameParameterWithoutPrefix(self) -> str:
		return self.parameter_without_prefix

	def getExpectTypes(self) -> Union[Text, Tuple[Required, Text]]:
		return self.parameter_types