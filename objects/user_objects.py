from typing import Union, List, Dict, Callable, Tuple, Callable, Any, get_args, get_origin, _SpecialForm
import discord

from .commands import commands_collection, dummyCommand
from utils import getCallSignature
from .stubs import ChannelMentionType

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

	def __init__(self, text: str, user_mentions: List[discord.abc.User], channel_mentions: List[Union[discord.abc.GuildChannel, discord.Thread]]) -> None:
		self.text = text
		self.user_mentions = user_mentions
		self.channel_mentions = channel_mentions
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

	def extractParametrs(self) -> None: # TODO обработка обязательных аргументов +
		# TODO кавычки как разделение + обработка пар параметров.
		received_parameters = getCallSignature(self.func)
		user_parametrs = list(self.copy_text.split()) if isinstance(self.copy_text, str)\
		else self.copy_text
		user_parametrs_cursor = 0
		while user_parametrs_cursor < len(user_parametrs):
			parametr_or_arg = user_parametrs[user_parametrs_cursor] # TODO user_parametr как отдельный класс, в котором при индексировании будут + курсоры сами.
			print("1", parametr_or_arg)
			user_parametrs_cursor += 1
			if parametr_or_arg.startswith("-"):
				parametr = parametr_or_arg
				arg = user_parametrs[user_parametrs_cursor]
				user_parametrs_cursor += 1
				print("2", arg)
				parametr_without_prefix = parametr.removeprefix("-")
				if parametr_without_prefix in received_parameters:
					parametr_types = received_parameters[parametr_without_prefix]
					check_types = []
					union_args = get_args(parametr_types)
					if union_args:
						for parametr_type in union_args:
							check_types.append(parametr_type)
					else:
						check_types.append(parametr_types)
					for check_type in check_types:
						try:
							converted_arg = check_type(arg)
							print(converted_arg)
						except:
							print("Ачибка!")
						else:
							received_parameters[parametr_without_prefix] = converted_arg
							break
			# else:
			# 	pass
				# arg = parametr_or_arg
				# for (parametr, parametr_type) in received_parameters.items():
				# 	if isinstance(arg, parametr_type):
				# 		received_parameters[parametr] = arg
				# 		break
				# else:
				# 	print("Ачибка!")


		# for (parametr, value) in received_parameters.items():
		# 	if "-" + parametr in user_args:
		# 		matching_arg_index = user_args.index("-" + parametr) # TODO здесь тоже
		# 		user_args.pop(matching_arg_index)
		# 		sent_parametr = user_args.pop(matching_arg_index + 1)
		# 	# elif value is TypeContent:
		# 	# 	received_parameters[parametr] = Content(" ".join(user_args[:]),
		# 	# 	self.guild_global_prefix, self.guild_access_prefix)
		# 	# 	user_args.clear()
		# 	elif user_args:
		# 		sent_parametr = user_args.pop(0) # TODO учёт аннотаций.
		# 	if value
		# 	if isinstance(sent_parametr, value):
		# 		received_parameters[parametr] = sent_parametr
		# 	else:
		# 		print("Еррур") # TODO
		# if user_args:
		# 	print("Еррур") # TODO
		# self.parametrs = received_parameters

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
		# method = self.content.getCommand()
		# parametrs = self.content.getParametrs()
		# await method(self.channel, **parametrs)