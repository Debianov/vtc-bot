from typing import Union, List, Dict, Callable, Tuple, Callable, Any
import discord

from .commands import commands_collection, dummyCommand
from utils import getCallSignature

class UserAction:

	def __init__(self, d_id: int, author: discord.Member,
	start_time: int) -> None:
		self.d_id = d_id
		self.author = author
		self.start_time = start_time
		self.finish_time: str
		self.result: str

class Guild:

	def __init__(self, global_prefix: str, access_prefix: str) -> None:
		self.global_prefix = global_prefix
		self.access_prefix = access_prefix

	def getGlobalPrefix(self) -> str:
		return self.global_prefix

	def getAccessPrefix(self) -> str:
		return self.access_prefix

class Content:

	def __init__(self, text: str) -> None:
		self.text = text
		self.func: Callable[[Any], None] = dummyCommand
		self.global_prefix: str = ""
		self.access_prefix: str = ""
		self.parametrs: Dict[str, str] = {}
		self.copy_text: str = ""

	def __str__(self) -> str:
		return self.text

	def createTextCopy(self) -> None:
		self.copy_text = self.text

	def getGlobalPrefix(self) -> str:
		return self.global_prefix

	def getParametrs(self) -> Dict[str, Union[List[str], str]]:
		return self.parametrs

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

	def extractCommand(self,
	name_extraction_object: Dict[str, Union[Callable[[Any], None],
	Dict[str, Callable[[Any], None]]]]) -> None: # TODO можно вместо str
	# TODO отдельный тип, где я юзаю оператор | для разделения различных версий
	# TODO имён команд.
	# TODO несколько команд в одной строке.
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

	def checkValueMatchToParametrType(self, value: Any, parametrType: Any) -> bool:
		if isinstance(parametrType, typing):
			# TODO нужно match на каждый type и соответствующие преобразования (попытки). В аннотациях свои типы лучше поставить. Только куда их классы ставить.

	def extractParametrs(self) -> None: # TODO обработка обязательных аргументов +
		# TODO кавычки как разделение + обработка пар параметров.
		received_parameters = getCallSignature(self.func)
		user_args = list(self.copy_text.split()) if isinstance(self.copy_text, str)\
		else self.copy_text
		for (parametr, value) in received_parameters.items():
			if "-" + parametr in user_args:
				matching_arg_index = user_args.index("-" + parametr) # TODO здесь тоже
				# TODO лучше учитывать аннотации.
				try:
					print(parametr, value, dir(value._typevar_types))
				except:
					print('Ачибка!')
				received_parameters[parametr] = user_args.pop(matching_arg_index + 1)
				user_args.pop(matching_arg_index)
			# elif value is TypeContent:
			# 	received_parameters[parametr] = Content(" ".join(user_args[:]),
			# 	self.guild_global_prefix, self.guild_access_prefix)
			# 	user_args.clear()
			elif not value and user_args:
				received_parameters[parametr] = user_args.pop(0) # TODO учёт аннотаций.
		if user_args:
			print("Еррур") # TODO
		self.parametrs = received_parameters

class UserMessage(UserAction):

	def __init__(self, d_id: int, author: discord.Member, start_time: int,
	guild: Guild, content: Content, channel: discord.TextChannel) -> None:
		super().__init__(d_id, author, start_time)
		self.guild = guild
		self.content = content
		self.channel = channel

	def isCommand(self) -> bool:
		self.content.extractGlobalPrefix(self.guild)
		if self.content.getGlobalPrefix():
			return True
		return False

	async def handle(self) -> None:
		pass

	async def reply(self) -> None:
		self.content.extractAccessPrefix(self.guild)
		self.content.extractCommand(commands_collection)
		self.content.extractParametrs()
		method = self.content.getCommand()
		parametrs = self.content.getParametrs()
		# await method(self.channel, **parametrs)