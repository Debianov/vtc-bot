"""
Основной модуль для сбора всех модулей и запуска бота.
"""

import asyncio
import os
from typing import Any, Dict, Optional, Union

import discord
import psycopg
from discord.ext import commands

from ._types import IDSupportObjects
from .exceptions import StartupBotError
from .help import BotHelpCommand
from .utils import ContextProvider, getEnvIfExist


class DBConnector:
	"""
	Основной класс для соединения с БД PostgreSQL.
	"""

	def __init__(
		self,
		**kwargs: str
	) -> None:
		self.conninfo: str = ""
		self.processArgs(kwargs)

	def processArgs(self, args: Dict[str, str]) -> None:
		matched_args = []
		for (key, value) in args.items():
			if value:
			matched_args.append(key + "=" + value)
		self.conninfo = " ".join(matched_args)

	async def initConnection(self) -> None:
		"""
		Функция для инициализации подключения к БД.
		"""
		self.dbconn = await psycopg.AsyncConnection.connect(
			self.conninfo,
			autocommit=True
		)

	def getDBconn(self) -> psycopg.AsyncConnection[Any]:
		return self.dbconn

class BotConstructor(commands.Bot):
	"""
	Класс для формирования экземпляра бота.
	"""

	def __init__(
		self,
		dbconn: Optional[psycopg.AsyncConnection[Any]] = None,
		context_provider: Optional[ContextProvider] = None,
		*args: Any,
		**kwargs: Any
	) -> None:
		self.dbconn = dbconn
		self.context_provider = context_provider
		super().__init__(*args, **kwargs)

	def run(self, *args: Any, **kwargs: Any) -> None:
		current_loop = asyncio.get_event_loop()
		current_loop.run_until_complete(self.prepare())
		super().run(*args, **kwargs)

	async def prepare(self) -> None:
		"""
		Метод для запуска механизмов инициализации
		компонентов бота. Обязателен к запуску, если не
		используется метод :attr:`run`.
		"""
		if self.dbconn and self.context_provider:
			await self._registerDBAdapters()
		await self._initCogs()

	async def _registerDBAdapters(self) -> None:

		context_provider = self.context_provider

		class DiscordObjectsDumper(psycopg.adapt.Dumper):
			"""
			Преобразовывает Discord-объекты в ID для записи в БД.
			"""

			def dump(
				self,
				elem: IDSupportObjects
			) -> bytes:
				return str(elem.id).encode()

		class DiscordObjectsLoader(psycopg.adapt.Loader):
			"""
			Преобразовывает записи из БД в объекты Discord.
			"""

			def load(
				self,
				data: bytes
			) -> Union[discord.abc.Messageable, discord.abc.Connectable, str]:
				string_data: str = data.decode()
				ctx = context_provider.getContext() # type: ignore [union-attr]
				for attr in ('get_member', 'get_user', 'get_channel'):
					try:
						result: Optional[discord.abc.Messageable] = getattr(
							ctx, attr)(int(string_data))
						if result:
							return result
					except (discord.DiscordException, AttributeError):
						continue
				return string_data

		self.dbconn.adapters.register_dumper( # type: ignore [union-attr]
			discord.abc.Messageable, DiscordObjectsDumper)
		self.dbconn.adapters.register_loader("bigint[]", # type: ignore [union-attr]
			DiscordObjectsLoader)

	async def _initCogs(self) -> None:
		for module_name in ("commands",):
			await self.load_extension(f"bot.{module_name}")

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
	if extract_envs := getEnvIfExist("POSTGRES_DBNAME", "POSTGRES_USER"):
		dbconn = loop.run_until_complete(DBConnFactory(
			dbname=extract_envs[0],
			user=extract_envs[1]
		))
	else:
		raise StartupBotError("Не удалось извлечь данные БД для подключения.")
	intents = discord.Intents.all()
	intents.dm_messages = False
	VCSBot = BotConstructor(
		dbconn=dbconn,
		context_provider=ContextProvider(),
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
	)
	VCSBot.run(os.getenv("DISCORD_API_TOKEN"))

if __name__ == "__main__":
	runForPoetry()