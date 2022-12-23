import typing
import discord
import inspect


class AssemblyArg(list): pass

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
		self.command: typing.Callable[..., typing.Any] # TODO typing
		self.parametrs: dict
		super().__init__(d_id, author, start_time)

	async def handle(self) -> None:
		if self.getGlobalPrefix():
			self.getAccessPrefix()
			self.command = self.getCommand()
			self.parametrs = self.getArguments()
			print(self.parametrs)
			await self.command(self.channel, **self.parametrs)
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
		for set_name in commands_collection:
			command_names = set_name.split("|")
			for command_name in command_names:
				if self.content.startswith(command_name):
					self.content = self.content.removeprefix(command_name + " ")
					return commands_collection[set_name]
		return dummy

	def getArguments(self) -> typing.Dict: # TODO обработка обязательных аргументов + кавычки как разделение. Для объединения двух практическ одинаковых методов можно поднять отдельный класс на content.
		received_parameters = getCallSignature(self.command)
		user_args = list(self.content.split())
		for (parametr, value) in received_parameters.items():
			if "-" + parametr in user_args:
				matching_arg_index = user_args.index("-" + parametr) # TODO здесь тоже лучше учитывать аннотации.
				received_parameters[parametr] = user_args.pop(matching_arg_index + 1)
				user_args.pop(matching_arg_index)
			elif value is AssemblyArg:
				received_parameters[parametr] = user_args[:]
				user_args.clear()
			elif not value and user_args:
				received_parameters[parametr] = user_args.pop(0) # TODO учёт аннотаций.
		if user_args:
			print("Еррур") # TODO
		self.resetContent()
		return received_parameters

	def resetContent(self) -> None:
		self.content = ""

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

class UserLog:

	def __init__(self):
		self.channel: discord.TextChannel = None # TODO DummyChannel

	async def create(self, name, target, act, d_in, output, priority, other: AssemblyArg):
		targetInstance = TargetLog(name, target, act, d_in, output, priority, other)
		return targetInstance

	async def __call__(self, channel: discord.TextChannel, point: str, point_args: AssemblyArg) -> None: # TODO обработка обязательных аргументов + кавычки как разделение
		point_func: typing.Callable = dummy # TODO Dummy check
		self.channel = channel
		for point_names in self.points_collection:
			point_names_collection = point_names.split("|")
			if point in point_names_collection:
				point_func = self.points_collection[point_names]
		received_parameters = getCallSignature(point_func)
		user_args = point_args
		for (parametr, value) in received_parameters.items():
			if "-" + parametr in user_args:
				matching_arg_index = user_args.index("-" + parametr) # TODO здесь тоже лучше учитывать аннотации.
				received_parameters[parametr] = user_args.pop(matching_arg_index + 1)
				user_args.pop(matching_arg_index)
			elif value is AssemblyArg:
				received_parameters[parametr] = user_args[:]
				user_args.clear()
			elif not value and user_args:
				received_parameters[parametr] = user_args.pop(0) # TODO учёт аннотаций.
		if user_args:
			print("Еррур") # TODO
		for value in received_parameters.values():
			if not value:
				print("Еррур") # TODO
		print(received_parameters)
		await point_func(self, **received_parameters)

	points_collection = {"create|cr|1": create} # TODO автозаполнение

class TargetLog: # TODO запись таргета в базу данных; механизм кэширования.

	def __init__(self, name: str, target: typing.Union[discord.Member, discord.CategoryChannel], act: str, d_in: typing.Union[discord.Member, discord.CategoryChannel], output: str, priority: int, other: AssemblyArg):
		self.name = name
		self.target = target
		self.act = act
		self.d_in = d_in
		self.output = output
		self.priority = priority
		self.other = other
		self.id = None # TODO генерация ID.
		self.matches: dict = {}

	def __setattr__(self, attr, nvalue): # TODO обработка нескольких пар имён.
		validateResult: typing.Union[bool, list]
		match attr:
			case "name":
				print("Name")
				# validateResult = self.validateNameParam(nvalue)
				# if not validateResult:
				# 	print("Еррур!") # TODO raise и в ост. ниже
			case "target":
				print("target")
				# if nvalue:
				# 	validateResult = self.validateTargetParam(nvalue)
				# else:
				# 	print("Еррур") # TODO
				# if not validateResult:
				# 	print("Еррур")
				# nvalue = validateResult
			case "act":
				print("act")
				# if nvalue:
				# 	validateResult = self.validateActParam(nvalue)
				# else:
				# 	print("Еррур")
				# if not validateResult:
				# 	print("Еррур")
				# nvalue = validateResult
			case "in":
				print("in")
				# if nvalue:
				# 	validateResult = self.validateInParam(nvalue)
				# else:
				# 	print("Еррур")
				# if not validateResult:
				# 	print("Еррур")
				# nvalue = validateResult
				# self.compareAttr()
			case "output":
				print("output")
				# validateResult = self.validateOutputParam(nvalue)
				# if not validateResult:
				# 	print("Еррур")
				# nvalue = validateResult
			case "priority":
				print("priority")
				# if nvalue:
				# 	validateResult = self.validatePriorityParam(nvalue)
				# else:
				# 	print("Еррур")
				# if not validateResult:
				# 	print("Еррур")
				# nvalue = validateResult
			case "other":
				print("other")
				# validateResult = self.validateOtherParam(nvalue)
				# if not validateResult:
				# 	print("Еррур")
				# nvalue = validateResult
		self.__dict__[attr] = nvalue

	def compareAttr(self):
		# TODO запрос из БД всех таргетов, но не более 50 самых редкоиспользуемых.
		TargetsLog = []
		for instance in TargetsLog:
			if self.act == instance.act:
				self.matches[instance.name or instance.ID] = self.act
			if self.target == instance.target:
				self.matches[instance.name or instance.ID] = self.target
			if self.d_in == instance._in:
				self.matches[instance.name or instance.ID] = self.d_in
			if self.name == instance.name:
				self.matches[instance.name or instance.ID] = self.name
		print(self.matches) # TODO
		self.submitSuggestionForMatch()

	def submitSuggestionForMatch(self):
		for attempt in range(3):
			print("Аба") # TODO
		else:
			print("Ачибка")

	def validateNameParam(self, value) -> bool:
		return list(value) in special_symbols
			
	def validateTargetParam(self, value) -> typing.Union[bool, list]:
		match value:
			case "all_channel":
				return # TODO все каналы гильдии на дальнейшую обработку.
			case "all_users":
				return # TODO все пользователи гильдии на дальнейшую обработку.
			case "all":
				return # TODO все каналы и пользователи гильдии
		if isinstance(value, discord.Member) or isinstance(value, discord.TextChannel): # TODO посмотреть, как объединить все типы каналов. Подобная
		# TODO проблема и в аннотациях.
			if value in []: # TODO проверка на вхождение в гильдию.
				return # TODO передача конкретного канала/пользователя (мн.ч) на дальнейшую обработку.
		else:
			print("Еррур")
		return False

	def validateActParam(self, value) -> typing.Union[bool, list]:
		return # TODO обработка по модулю прав. Возврат списка

	def validateInParam(self, value) -> typing.Union[bool, list]:
		match value:
			case "df":
				return # TODO извлекаем канал по умолчанию
		if isinstance(value, discord.Member) or isinstance(value, discord.TextChannel): # TODO посмотреть, как объединить все типы каналов. Подобная
		# TODO проблема и в аннотациях.
			if value in []: # TODO проверка на вхождение в гильдию.
				return # TODO передача конкретного канала/пользователя (мн.ч) на дальнейшую обработку.
		else:
			print("Еррур")

	def validateOutputParam(self, value):
		return # TODO передача шаблона.

	def validatePriorityParam(self, value):
		match value:
			case "-1":
				return # TODO в конец очереди
		if value.isDigit():
			return # TODO возврат числа
		else:
			return False # TODO возврат ошибки.

	def validateOtherParam(self, value):
		return # TODO отсылочка на модуль разграничения прав.

async def dummy(channel: discord.TextChannel):
	await channel.send("Не очень успешно!")

async def pointDummy(channel: discord.TextChannel):
	await channel.send("Да тоже херня какая-то")

def getCallSignature(instance) -> typing.Dict:
	result: dict = {}
	check_obj = instance.__call__ if inspect.isclass(instance) else instance

	for key in inspect.getfullargspec(check_obj).args:
		if key != "channel" and key != "self":
			result[key] = ""
	annot_args = inspect.getfullargspec(check_obj).annotations
	for (key, value) in annot_args.items():
		if value is AssemblyArg:
			result[key] = value
	return result

def getKeyByValue(collection: dict, check_value: typing.Any) -> typing.Dict[typing.Union[str, int], typing.Union[str, int]]:
	new_collection = {}
	for (key, value) in collection.items():
		if value == check_value:
			new_collection[key] = value
	return new_collection

commands_collection = {"logs|log": UserLog()}

special_symbols = ["+", "-", "%", ">"]