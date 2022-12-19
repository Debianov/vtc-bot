import typing
import discord

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

class UserMessage(UserAction, discord.Message):

	def __init__(self, d_id: int, author: discord.Member, guild: Guild, 
	content: str, channel: discord.TextChannel, start_time: int) -> None:
		self.guild = guild
		self.content = content
		self.channel = channel
		super().__init__(d_id, author, start_time)

	async def handle(self) -> None:
		if self.getGlobalPrefix():
			self.getAccessPrefix()
			command = self.getCommand()
			await command(self.channel)
			# self.determineArguments()
		# else:
		# 	... # TODO антиспам, антифлуд, логирование и проч., и проч.

	def getGlobalPrefix(self) -> str:
		if self.content.startswith(self.guild.global_prefix):
			self.content = self.content.removeprefix(self.guild.global_prefix + " ")
			return self.guild.global_prefix
		else:
			return "" # TODO дописывать декоратором.

	def getAccessPrefix(self) -> str:
		if self.content.startswith(self.guild.access_prefix):
			self.content = self.content.removeprefix(self.guild.access_prefix + " ")
			return self.guild.access_prefix
		else:
			return ""

	def getCommand(self) -> typing.Callable:
		for command_name in commands_collection:
			if self.content.startswith(command_name):
				self.content = self.content.removeprefix(command_name + " ")
				return commands_collection[command_name]
		return dummy

	# def determineArguments(self):
	# 	if self.content in arguments_collection: # TODO какую
	# TODO часть сообщения проверить? А на вхождение чего?
	# 		... # TODO чё-то удалить
	# 		return self.content

class ActElement:

	def __init__(self) -> None:
		self.checking_symbol: str
		self.bind_act: str

	def determineAct(self) -> None:
		match self.checking_symbol:
			case '+':
				self.bind_act = "ADD"
			case '-':
				self.bind_act = "DELETE"
			case '>':
				self.bind_act = "CHANGE"

async def test(channel: discord.TextChannel) -> None:
	await channel.send("Успешно!")

async def dummy(channel: discord.TextChannel):
	await channel.send("Не очень успешно!")

commands_collection = {"test": test}