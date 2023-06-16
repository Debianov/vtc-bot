"""
Основной модуль для сбора всех модулей и запуска бота.
"""

import discord
import logging
import psycopg
from typing import Optional, Union, Tuple, Union, Optional, Any
from discord.ext import commands
import asyncio
import logging
from .utils import ContextProvider
import os

from .help import BotHelpCommand
class DBConnector:
	"""
	Основной класс для соединения с БД PostgreSQL.
	"""

	def __init__(
		self,	
		# dbname: str,
		# dbuser: str,
		**kwargs: str
	) -> None:
		self.conninfo: str = ""
		self.processArgs(kwargs)

	def processArgs(self, args: Dict[str, str]) -> None:
		matched_args = []
		for (key, value) in args.items():
			matched_args.append(key + "=" + value)
		self.conninfo = " ".join(matched_args)

	async def initConnection(self) -> None:
		"""
		Функция для инициализации подключения к БД.
		"""
		self.dbconn = await psycopg.AsyncConnection.connect(f"host={self.dbhost} port={self.dbport} password={self.dbpassword}", autocommit=True)

	def getDBconn(self) -> psycopg.AsyncConnection[Any]:
		return self.dbconn

class BotConstructor(commands.Bot):
	"""
	Класс для формирования экземпляра бота.
	"""

	def __init__(
			self,
			dbconn: psycopg.AsyncConnection[Any] = None,
			context_provider: ContextProvider = None,
			*args: Any,
			**kwargs: Any
		):
		self.dbconn = dbconn
		self.context_provider = context_provider
		super().__init__(*args, **kwargs)

	def run(self, *args: Any, **kwargs: Any) -> None:
		current_loop = asyncio.get_event_loop()
		current_loop.run_until_complete(self.prepare())
		super().run(*args, **kwargs)

	async def prepare(self) -> None:
		"""
		Метод для запуска механизмов инициализации компонентов бота. Обязателен к запуску,
		если не используется метод :attr:`run`.
		"""
		if self.dbconn:
			await self.registerDBAdapters()
		await self.initCogs()

	async def registerDBAdapters(self) -> None:

		context_provider = self.context_provider
		class DiscordObjectsDumper(psycopg.adapt.Dumper):
			"""
			Преобразовывает Discord-объекты в ID для записи в БД.
			"""
			def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> bytes:
				return str(elem.id).encode()

		class DiscordObjectsLoader(psycopg.adapt.Loader):
			"""
			Преобразовывает записи из БД в объекты Discord.
			"""

			def load(self, data: bytes) -> Union[discord.abc.Messageable, discord.abc.Connectable, str]: 
				string_data: str = data.decode()
				ctx = context_provider.getContext()
				for attr in ('get_member', 'get_user', 'get_channel'):
					try:
						result: Optional[discord.abc.Messageable] = getattr(
							ctx, attr)(int(string_data))
						if result:
							return result
					except (discord.DiscordException, AttributeError):
						continue
				return string_data
				
		self.dbconn.adapters.register_dumper(discord.abc.Messageable, DiscordObjectsDumper)
		self.dbconn.adapters.register_loader("bigint[]", DiscordObjectsLoader)

	async def initCogs(self) -> None:
		for module_name in ("commands",):
			await self.load_extension(f"bot.{module_name}")
		for cog_name in self.cogs:
			cog = self.get_cog(cog_name)
			cog.dbconn = self.dbconn
			cog.context_provider = self.context_provider

async def DBConnFactory(**kwargs: str) -> psycopg.AsyncConnection[Any]:
	"""
	Фабрика для создания готового подключения к БД PostgreSQL.

	Returns:
		psycopg.AsyncConnection[Any]
	"""
	dbconn_instance = DBConnector(**kwargs)
	await dbconn_instance.initConnection()
	return dbconn_instance.getDBconn()

def runForPoetry() -> None:
	loop = asyncio.get_event_loop()
	dbconn = loop.run_until_complete(DBConnFactory(dbhost=os.getenv("POSTGRES_HOST"),
	dbport=os.getenv("POSTGRES_PORT"), dbpassword=os.getenv("POSTGRES_PASSWORD")))
	intents = discord.Intents.all()
	intents.dm_messages = False
	VCSBot = BotConstructor(
		dbconn=dbconn,
		context_provider=ContextProvider(),
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
	)
	VCSBot.run(os.getenv("DISCORD_API_SEC"))

if __name__ == "__main__":
	runForPoetry()