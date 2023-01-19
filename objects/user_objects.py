from typing import Union, List, Dict, Callable, Tuple, Callable, Any, get_args, get_origin, _SpecialForm, Final
from types import UnionType
import discord

from .commands import commands_collection, dummyCommand, Required, ActText
from utils import getCallSignature
from .stubs import Text, ChannelMentionText, DummyText, WrongTextTypeSignal, WrongActSignal

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

	async def handle(self) -> None:
		pass

	async def reply(self) -> None:
		self.content.extractAccessPrefix(self.guild)
		self.content.extractCommand(commands_collection)
		self.content.extractParameters()
		method = self.content.getCommand()
		parameters = self.content.getParameters()
		# await method(self.channel, **parameters)

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

	def __init__(self, text: str, user_mentions: List[discord.abc.User], channel_mentions: List[Union[discord.abc.GuildChannel]]) -> None: # TODO discord.Thread не могу вставить в Union: нету атрибута такого, хотя по докам всё сходится.
		self.text = text
		self.user_mentions = user_mentions
		self.channel_mentions = channel_mentions
		self.func: Callable[[Any], None] = dummyCommand
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

	def getParameters(self) -> Dict[str, Union[List[str], str]]:
		return self.parameters

	def getCommand(self) -> Callable[[Any], None]:
		return self.func

	def extractGlobalPrefix(self, guild: Guild) -> None:
		if not self.copy_text:
			self.createTextCopy()
		if self.copy_text.startswith(guild.getGlobalPrefix()):
			self.copy_text = self.copy_text.removeprefix(guild.getGlobalPrefix() + " ")
			self.global_prefix = guild.getGlobalPrefix()

	def extractAccessPrefix(self, guild: Guild) -> None:
		if not self.copy_text:
			self.createTextCopy()
		if self.copy_text.startswith(guild.getAccessPrefix()):
			self.copy_text = self.copy_text.removeprefix(guild.getAccessPrefix() + " ")
			self.access_prefix = guild.getAccessPrefix()

	def extractCommand(self, name_extraction_object: Dict[str,
	Union[Callable[[Any], None], Dict[str, Callable[[Any], None]]]]) -> None:
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

	def extractParameters(self) -> None: # TODO кавычки как разделение +
		# TODO обработка пар параметров. 
		#? форму object -parameter object object допускать?
		self.parameters = all_parameters_current_command =\
		getCallSignature(self.func)
		found_parameters: Dict[str, Text] = {}
		split_user_text = self.copy_text.split()
		split_user_text_cursor = 0
		while split_user_text_cursor < len(split_user_text):
			parameter_or_parameter_arg = split_user_text[split_user_text_cursor] # TODO
			# TODO user_parameter как отдельный класс-струтктура данных, в котором при
			# TODO индексировании будут + курсоры сами.
			split_user_text_cursor += 1
			if parameter_or_parameter_arg.startswith("-"): # TODO баг: -object может быть распознан как параметр.
				parameter = parameter_or_parameter_arg
				found_parameters.update(self.extractExplicitParameter(parameter,
				split_user_text, split_user_text_cursor))
			else:
				parameter_arg = parameter_or_parameter_arg
				found_parameters.update(self.extractImplicitParameter(parameter_arg))
		# print(self.parameters)
		self.checkForMissingRequiredParameters()

	def extractExplicitParameter(self, parameter: str, split_user_text: List[str],
	split_user_text_cursor: int) -> Dict[str, Text]:
		arg = split_user_text[split_user_text_cursor]
		found_parameters: Dict[str, Text] = {}
		split_user_text_cursor += 1
		parameter_without_prefix = parameter.removeprefix("-")
		if parameter_without_prefix in self.parameters:
			parameter_types = self.parameters[parameter_without_prefix]
			converted_arg = self.convertedArg(parameter, parameter_types, arg)
			self.checkConvertedArg(converted_arg, parameter, found_parameters)
		return found_parameters

	def extractImplicitParameter(self, arg: str) -> Dict[str, Text]:
		found_parameters: Dict[str, Text] = {}
		for (parameter, parameter_types) in self.parameters.items():
			converted_arg = self.convertedArg(parameter, parameter_types, arg)
			if self.checkConvertedArg(converted_arg, parameter, found_parameters):
				break
		self.parameters.pop(parameter)
		return found_parameters

	def checkForMissingRequiredParameters(self) -> None:
		maybe_missing_required_parameters = self.parameters
		for (parameter, parameter_types) in\
		maybe_missing_required_parameters.items():
			if Required in parameter_types: # TODO parameter_type может быть не tupl-ом.
				raise DeterminingParameterError(list(maybe_missing_required_parameters.
				keys())[0])

	def convertedArg(self, parameter: str, parameter_types: Union[Text,
	Tuple[Required, Text]], target_arg: str) -> Text:
		check_types: List[Text] = []
		self.generateCheckTypes(parameter_types, check_types)
		for check_type in check_types:
			try:
				converted_arg = check_type(target_arg)
			except WrongTextTypeSignal:
				pass
			except WrongActSignal:
				raise ActParameterError(parameter)
			else:
				return converted_arg

	def generateCheckTypes(self, parameter_types: Union[Text, Tuple[Required, Text]], check_types: List[Text]) -> None:
		if isinstance(parameter_types, tuple) and parameter_types is not Required: # Required не трогаем. Он проверяется отдельно (checkForNotFoundParameters).
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

class DeterminingParameterError(Exception):
	
	def __init__(self, error_parameter: str):
		self.error_parameter = error_parameter
		self.processParameterName()
		self.error_text = "Убедитесь, что вы указали все обязательные аргументы, либо указали параметры явно. Не найденные параметры: {}".format(self.error_parameter) # TODO embedded

	def getErrorText(self) -> str:
		return self.error_text

	def processParameterName(self) -> None:
		if self.error_parameter.startswith("d_"):
			self.error_parameter = self.error_parameter.removeprefix("d_")

class ActParameterError(Exception):

	def __init__(self, error_parameter: str):
		self.error_parameter = error_parameter
		self.processParameterName()
		self.error_text = "Убедитесь, что вы указали знак действия в параметре {}".format(self.error_parameter) # TODO embedded

	def getErrorText(self) -> str:
		return self.error_text

	def processParameterName(self) -> None:
		if self.error_parameter.startswith("d_"):
			self.error_parameter = self.error_parameter.removeprefix("d_")