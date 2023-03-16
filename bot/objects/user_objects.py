from typing import Union, List, Dict, Tuple, Callable, Any, get_args,\
get_origin
from types import UnionType
import discord

from .commands import commands_collection, dummyCommand, Required
from bot.utils import getCallSignature, ArgAndParametersList
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

	async def handle(self) -> None:
		pass

	async def reply(self) -> None:
		self.content.extractCommand(commands_collection)
		self.content.extractParameters()
		method = self.content.getCommand()
		parameters = self.content.getParameters()
		await method(self.channel, **parameters)

	async def reply_by_custome_text(self, text: str) -> None:
		await self.channel.send(text)

	def isCommand(self) -> bool:
		self.content.extractGlobalPrefix(self.guild)
		if self.content.getGlobalPrefix():
			return True
		return False

class Guild:

	def __init__(self, global_prefix: str, access_prefix: str) -> None:
		self.global_prefix = global_prefix
		self.access_prefix = access_prefix

	def getGlobalPrefix(self) -> str:
		return self.global_prefix

	def getAccessPrefix(self) -> str:
		return self.access_prefix

class Content:

	def __init__(self, text: str) -> None: # TODO
	# discord.Thread не могу вставить в Union: нету атрибута такого, хотя по
	# докам всё сходится.
		self.text = text
		self.current_global_prefix = current_global_prefix
		self.current_access_prefix = current_access_prefix
		self.func: Callable[..., None] = dummyCommand
		self.global_prefix: str = ""
		self.access_prefix: str = ""
		self.parameters: Dict[str, Text] = {}
		self.copy_text: str = ""

	def __str__(self) -> str:
		return self.text

	def createTextCopy(self) -> None:
		self.copy_text = self.text

	def getGlobalPrefix(self) -> str:
		return self.global_prefix

	def getAccessPrefix(self) -> str:
		return self.access_prefix

	def getParameters(self) -> Dict[str, Text]:
		return self.found_parameters

	def getCommand(self) -> Callable[[Any], None]:
		return self.func

	def extractPrefixes(self) -> None:
		if not self.copy_text:
			self.createTextCopy()
		self.extractGlobalPrefix()
		self.extractAccessPrefix()
		self.removeSpaceAfterPrefixes()

	def extractGlobalPrefix(self) -> None:
		if not self.global_prefix:
			if self.copy_text.startswith(self.current_global_prefix):
				self.copy_text = self.copy_text.removeprefix(self.current_global_prefix)
				self.global_prefix = self.current_global_prefix

	def extractAccessPrefix(self) -> None:
		if not self.access_prefix:
			if self.copy_text.startswith(self.current_access_prefix):
				self.copy_text = self.copy_text.removeprefix(self.current_access_prefix + " ")
				self.access_prefix = self.current_access_prefix

	def removeSpaceAfterPrefixes(self) -> None:
		self.copy_text = self.copy_text.removeprefix(" ")

	def extractCommand(self, name_extraction_object:
		Dict[str, Union[Callable[..., None], Dict[str,
		Callable[..., None]]]]) -> None:
		# TODO сделать особый тип str, где есть разделение |, которое используется в
		# распознавании алиасов одной и той же команды.
		# TODO и тут в name_extraction_object аннотация слишком большая. Не создать
		# ли нам generic?
		for extract_name in name_extraction_object:
			command_names = extract_name.split("|")
			for command_name in command_names:
				if self.copy_text.startswith(command_name):
					self.copy_text = self.copy_text.removeprefix(command_name + " ")
					value = name_extraction_object[extract_name]
					if isinstance(value, dict):
						self.extractCommand(value)
					else:
						self.func = value
					break

	def extractParameters(self) -> None: # TODO обработка пар параметров.
		self.parameters = all_parameters_current_command =\
		getCallSignature(self.func)
		self.found_parameters: Dict[str, Text] = {}
		self.unfound_args: List[str] = []
		self.args_with_wrong_text_type: Dict[str, List[Tuple[str, Text]]] = {}
		self.split_user_text = ArgAndParametersList(self.copy_text.split())
		while self.split_user_text:
			parameter_or_parameter_arg = self.split_user_text.popWithSpaceRemoving(0)
			if parameter_or_parameter_arg.startswith("-"): # TODO баг: -object может
				# быть распознан как параметр.
				parameter = parameter_or_parameter_arg
				self.extractExplicitParameter(parameter)
			else:
				parameter_arg = parameter_or_parameter_arg
				parameter_arg = self.extractArgsGroup(parameter_arg)
				self.extractImplicitParameter(parameter_arg)
		self.checkUnfoundArgs()
		self.checkForMissingRequiredParameters()
		self.extendParametersByOptionalParameters()

	def extractExplicitParameter(self, parameter: str) -> None:
		arg = self.split_user_text.popWithSpaceRemoving(0)
		arg = self.extractArgsGroup(arg)
		found_parameters: Dict[str, Text] = {}
		parameter_without_prefix = parameter.removeprefix("-")
		if parameter_without_prefix in self.parameters:
			parameter_types = self.parameters[parameter_without_prefix]
			converted_args = self.convertedArg(parameter, parameter_types, arg)
			if converted_args:
				self.found_parameters[parameter_without_prefix] = converted_args
				self.parameters.pop(parameter_without_prefix)
			else:
				self.unfound_args.append(arg)

	def extractImplicitParameter(self, arg: str) -> None: # TODO честно
		# говоря, в этих двух методах назревает мысль создать отдельный класс для
		# arg.
		found_parameters: Dict[str, Text] = {}
		for (parameter, parameter_types) in self.parameters.items():
			converted_args = self.convertedArg(parameter, parameter_types, arg)
			if converted_args:
				self.found_parameters[parameter] = converted_args
				self.parameters.pop(parameter)
				break
		else:
			self.unfound_args.append(arg)

	def extractArgsGroup(self, args_or_arg: str) -> str:
		args: str = ""
		if self.isArgsGroup(args_or_arg):
			args = args_or_arg.removeprefix("\"")
			while True:
				args += " " + self.split_user_text.popWithSpaceRemoving(0)
				if args.endswith("\""): # TODO bag zone + сделать ошибку для группы аргументов
					break
			args = args.removesuffix("\"")
		return args or args_or_arg

	def isArgsGroup(self, args_or_arg: str) -> bool:
		if args_or_arg.startswith("\""): # TODO метод проверки нужно будет поменять (ну или подумать над ним хотя б).
			return True
		return False

	def convertedArg(self, parameter: str, parameter_types: Union[Text,
	Tuple[Required, Text]], arg: str) -> str:
		check_types: List[Text] = []
		converted_args: List[str] = []
		self.generateCheckTypes(parameter_types, check_types)
		arg_or_args: List[str] = arg.split() # TODO а зачем тогда мы их в строку переводим, если они здесь разбиваются в список?
		for check_type in check_types:
			for arg in arg_or_args:
				try:
					converted_arg_instance = check_type(arg) # TODO нейминги.
					converted_arg_instance.checkText()
					converted_arg_instance.processText()
					converted_args.append(converted_arg_instance.getProcessedText())
				except WrongTextTypeSignal:
					self.args_with_wrong_text_type.setdefault(arg, []).append(
					(parameter, check_type))
				except WrongActSignal:
					raise ActParameterError(parameter)
		return " ".join(converted_args)

	def generateCheckTypes(self, parameter_types: Union[Text, Tuple[Required,
	Text]], check_types: List[Text]) -> None:
		if isinstance(parameter_types, tuple) and parameter_types is not Required:
			# Required не трогаем. Он проверяется отдельно (checkForNotFoundParameters).
			for parameter_type in parameter_types:
				if self.isUnionType(parameter_type):
					check_types.extend(self.extractUnionType(parameter_type))
				elif issubclass(parameter_type, Text):
					check_types.append(parameter_type)
		else:
			check_types.append(parameter_types)

	def isUnionType(self, parameter_type: Union[UnionType, Text, Required])\
	-> bool:
		if get_origin(parameter_type) is Union:
			return True
		return False

	def extractUnionType(self, parameter_type: Union) -> List[Text]:
		union_args = get_args(parameter_type)
		result: List[Text] = []
		for parameter_type in union_args:
			result.append(parameter_type)
		return result

	def checkUnfoundArgs(self) -> None:
		if not self.unfound_args:
			return
		for unfound_arg in self.unfound_args:
			if unfound_arg in self.args_with_wrong_text_type:
				raise UnmatchingParameterTypeError(unfound_arg,
				self.args_with_wrong_text_type.get(unfound_arg)[0]) # TODO вывод типов, которые, возможно, имелись ввиду, организовать.

	def checkForMissingRequiredParameters(self) -> None:
		maybe_missing_required_parameters = self.parameters
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
			if parameter not in self.found_parameters:
				self.found_parameters.update({parameter: ""})