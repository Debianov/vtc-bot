from typing import Union
import discord

class UserLog:

	# def __init__(self) -> None:
	# 	# self.channel: discord.TextChannel = ""
	# 	# self.command: typing.Callable[[discord.TextChannel], None] = dummyCommand # TODO проработать dummy
	# 	# self.content: = ""
	# 	# TODO Dummy
	# 	# self.parametrs: dict = {}

	@staticmethod
	async def create(channel: discord.TextChannel, name: Union[str, int], target: Union[discord.TextChannel, discord.Member], act: Union[str, int], d_in: Union[discord.TextChannel, discord.Member], 
	priority: int, output: Union[str, int], other: Union[str, int]) -> None:
		print(name, target, other)
		# targetInstance = TargetLog(name, target, act, d_in, output, priority, other)
		# return targetInstance

	# async def __call__(self, channel: discord.TextChannel,
	# remaining_content: Content) -> None: # TODO обработка обязательных
	# # TODO аргументов + кавычки как разделение
	# 	self.channel = channel
	# 	self.content = remaining_content #! якорь
	# 	# self.getCommand(point)
	# 	self.content.handle(self.points_collection)
	# 	await self.content.command(self.channel, **self.content.parametrs)
	# 	# parserInstance = MenuParametrParser(point, point_args, self.points_collection) # TODO тут проблемка с тайпингом.
	# 	# self.command = parserInstance.getCommand()
	# 	# self.parametrs = parserInstance.getParametrs()
	# 	# await self.command(self, **self.parametrs)

class DummyTextChannel:
	pass # TODO

async def dummyCommand(channel: discord.TextChannel) -> None:
	await channel.send("Не очень успешно!")

# class TargetLog: # TODO запись таргета в базу данных; механизм кэширования.

# 	def __init__(self, name: str, target: typing.Union[discord.Member, discord.CategoryChannel], act: str, d_in: typing.Union[discord.Member, discord.CategoryChannel], output: str, priority: int, other: AssemblyArg):
# 		self.name = name
# 		self.target = target
# 		self.act = act
# 		self.d_in = d_in
# 		self.output = output
# 		self.priority = priority
# 		self.other = other
# 		self.id = None # TODO генерация ID.
# 		self.matches: dict = {}

# 	def __setattr__(self, attr, nvalue): # TODO обработка нескольких пар имён.
# 		validateResult: typing.Union[bool, list]
# 		match attr:
# 			case "name":
# 				print("Name")
# 				# validateResult = self.validateNameParam(nvalue)
# 				# if not validateResult:
# 				# 	print("Еррур!") # TODO raise и в ост. ниже
# 			case "target":
# 				print("target")
# 				# if nvalue:
# 				# 	validateResult = self.validateTargetParam(nvalue)
# 				# else:
# 				# 	print("Еррур") # TODO
# 				# if not validateResult:
# 				# 	print("Еррур")
# 				# nvalue = validateResult
# 			case "act":
# 				print("act")
# 				# if nvalue:
# 				# 	validateResult = self.validateActParam(nvalue)
# 				# else:
# 				# 	print("Еррур")
# 				# if not validateResult:
# 				# 	print("Еррур")
# 				# nvalue = validateResult
# 			case "in":
# 				print("in")
# 				# if nvalue:
# 				# 	validateResult = self.validateInParam(nvalue)class DummyTextChannel:
	pass # TODO
# 				# else:
# 				# 	print("Еррур")
# 				# if not validateResult:
# 				# 	print("Еррур")
# 				# nvalue = validateResult
# 				# self.compareAttr()
# 			case "output":
# 				print("output")
# 				# validateResult = self.validateOutputParam(nvalue)
# 				# if not validateResult:
# 				# 	print("Еррур")
# 				# nvalue = validateResult
# 			case "priority":
# 				print("priority")
# 				# if nvalue:
# 				# 	validateResult = self.validatePriorityParam(nvalue)
# 				# else:
# 				# 	print("Еррур")
# 				# if not validateResult:
# 				# 	print("Еррур")
# 				# nvalue = validateResult
# 			case "other":
# 				print("other")
# 				# validateResult = self.validateOtherParam(nvalue)
# 				# if not validateResult:
# 				# 	print("Еррур")
# 				# nvalue = validateResult
# 		self.__dict__[attr] = nvalue

# 	def compareAttr(self):
# 		# TODO запрос из БД всех таргетов, но не более 50 самых редкоиспользуемых.
# 		TargetsLog = []
# 		for instance in TargetsLog:
# 			if self.act == instance.act:
# 				self.matches[instance.name or instance.ID] = self.act
# 			if self.target == instance.target:
# 				self.matches[instance.name or instance.ID] = self.target
# 			if self.d_in == instance._in:
# 				self.matches[instance.name or instance.ID] = self.d_in
# 			if self.name == instance.name:
# 				self.matches[instance.name or instance.ID] = self.name
# 		print(self.matches) # TODO
# 		self.submitSuggestionForMatch()

# 	def submitSuggestionForMatch(self):
# 		for attempt in range(3):
# 			print("Аба") # TODO
# 		else:
# 			print("Ачибка")

# 	def validateNameParam(self, value) -> bool:
# 		return list(value) in special_symbols
			
# 	def validateTargetParam(self, value) -> typing.Union[bool, list]:
# 		match value:
# 			case "all_channel":
# 				return # TODO все каналы гильдии на дальнейшую обработку.
# 			case "all_users":
# 				return # TODO все пользователи гильдии на дальнейшую обработку.
# 			case "all":
# 				return # TODO все каналы и пользователи гильдии
# 		if isinstance(value, discord.Member) or isinstance(value, discord.TextChannel): # TODO посмотреть, как объединить все типы каналов. Подобная
# 		# TODO проблема и в аннотациях.
# 			if value in []: # TODO проверка на вхождение в гильдию.
# 				return # TODO передача конкретного канала/пользователя (мн.ч) на дальнейшую обработку.
# 		else:
# 			print("Еррур")
# 		return False

# 	def validateActParam(self, value) -> typing.Union[bool, list]:
# 		return # TODO обработка по модулю прав. Возврат списка

# 	def validateInParam(self, value) -> typing.Union[bool, list]:
# 		match value:
# 			case "df":
# 				return # TODO извлекаем канал по умолчанию
# 		if isinstance(value, discord.Member) or isinstance(value, discord.TextChannel): # TODO посмотреть, как объединить все типы каналов. Подобная
# 		# TODO проблема и в аннотациях.
# 			if value in []: # TODO проверка на вхождение в гильдию.
# 				return # TODO передача конкретного канала/пользователя (мн.ч) на дальнейшую обработку.
# 		else:
# 			print("Еррур")

# 	def validateOutputParam(self, value):
# 		return # TODO передача шаблона.

# 	def validatePriorityParam(self, value):
# 		match value:
# 			case "-1":
# 				return # TODO в конец очереди
# 		if value.isDigit():
# 			return # TODO возврат числа
# 		else:
# 			return False # TODO возврат ошибки.

# 	def validateOtherParam(self, value):
# 		return # TODO отсылочка на модуль разграничения прав.

commands_collection = {"logs|log": {"create|cr|1": UserLog.create}} # TODO автоматическое формирование словаря.