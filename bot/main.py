"""
The main module that collects all the modules and starting the bot.
"""

import asyncio
import logging
import logging.handlers
import os
from typing import Any, Dict, Optional, Union

import discord
import psycopg
from discord.ext import commands

from ._types import IDObjects
from .exceptions import StartupBotError
from .help import BotHelpCommand
from .mock import Mock, MockAsyncConnection
from .utils import ContextProvider, getEnvIfExist


def _init_logging() -> None:
	logger = logging.getLogger('discord')
	logger.setLevel(logging.DEBUG)
	logging.getLogger('discord.http').setLevel(logging.INFO)

	handler = logging.handlers.RotatingFileHandler(
		filename='vtc-bot.log',
		encoding='utf-8',
		maxBytes=32 * 1024 * 1024,  # 32 MiB
		backupCount=5,  # Rotate through 5 files
	)
	dt_fmt = '%Y-%m-%d %H:%M:%S'
	formatter = logging.Formatter(
		'[{asctime}] [{levelname:<8}] {module_func}: {message}',
		dt_fmt, style='{')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

class DBConnector:
	"""
	The main class for connecting to a PostgresSQL database.
	"""

	def __init__(
		self,
		**kwargs: str
	) -> None:
		self.conninfo: str = ""
		self._processArgs(kwargs)

	def _processArgs(self, args: Dict[str, str]) -> None:
		matched_args = []
		for (key, value) in args.items():
			matched_args.append(key + "=" + value)
		self.conninfo = " ".join(matched_args)

	async def initConnection(self) -> None:
		"""
		The function for initializing a PostgresSQL database connection.
		"""
		self.dbconn = await psycopg.AsyncConnection.connect(
			self.conninfo,
			autocommit=True
		)

	def getDBconn(self) -> psycopg.AsyncConnection[Any]:
		return self.dbconn


class BotConstructor(commands.Bot):
	"""
	The class for constructing the bot instance.
	"""

	def __init__(
		self,
		dbconn: psycopg.AsyncConnection[Any] = MockAsyncConnection(),
		context_provider: ContextProvider = ContextProvider(),
		cog_load: bool = True,
		*args: Any,
		**kwargs: Any
	) -> None:
		self.dbconn = dbconn
		self.context_provider = context_provider
		self.cog_load = cog_load
		super().__init__(*args, **kwargs)

	def run(self, *args: Any, **kwargs: Any) -> None:
		current_loop = asyncio.get_event_loop()
		current_loop.run_until_complete(self.prepare())
		super().run(*args, **kwargs)

	async def prepare(self) -> None:
		"""
		The method starts the initialization mechanism of bot
		components. Needs to be called if the high-level method :attr:`run`
		isn't called.
		"""
		if not isinstance(self.dbconn, Mock) and self.context_provider:
			await self._registerDBAdapters()
		if self.cog_load:
			await self._initCogs()

	async def _registerDBAdapters(self) -> None:

		context_provider = self.context_provider

		class DiscordObjectsDumper(psycopg.adapt.Dumper):
			"""
			This adapter converts `discord.abc.Messageable <https://discord
			py.readthedocs.io/en/stable/api.html?highlight=messageable#disco
			rd.abc.Messageable>`_ to a str in the PostgresSQL database.
			"""

			def dump(
				self,
				elem: IDObjects
			) -> bytes:
				return str(elem.id).encode()

		class DiscordObjectsLoader(psycopg.adapt.Loader):
			"""
			This adapter converts str to a discord object.
			"""

			def load(
				self,
				data: bytes
			) -> Union[
				discord.abc.Messageable, discord.abc.Connectable, str]:
				string_data: str = data.decode()
				ctx = context_provider.getContext()  # type: ignore [union-attr]
				for attr in ('get_member', 'get_user', 'get_channel'):
					try:
						result: Optional[discord.abc.Messageable] = getattr(
							ctx, attr)(int(string_data))
						if result:
							return result
					except (discord.DiscordException, AttributeError):
						continue
				return string_data

		self.dbconn.adapters.register_dumper(  # type: ignore [union-attr]
			discord.abc.Messageable, DiscordObjectsDumper)
		self.dbconn.adapters.register_loader("bigint[]", # type: ignore [union-attr]
			DiscordObjectsLoader)

	async def _initCogs(self) -> None:
		for module_name in ("commands",):
			await self.load_extension(f"bot.{module_name}")


async def DBConnFactory(**kwargs: str) -> psycopg.AsyncConnection[Any]:
	"""
	The factory for creating a done connection to the PostgresSQL database.

	Returns:
		psycopg.AsyncConnection[Any]
	"""
	dbconn_instance = DBConnector(**kwargs)
	await dbconn_instance.initConnection()
	return dbconn_instance.getDBconn()


def runForPoetry() -> None:
	_init_logging()
	loop = asyncio.get_event_loop()
	if extract_envs := getEnvIfExist("POSTGRES_DBNAME", "POSTGRES_USER"):
		dbconn = loop.run_until_complete(DBConnFactory(
			dbname=extract_envs[0],
			user=extract_envs[1]
		))
	else:
		raise StartupBotError(
			"Не удалось извлечь данные БД для подключения.")
	intents = discord.Intents.all()
	intents.dm_messages = False
	VCSBot = BotConstructor(
		dbconn=dbconn,
		context_provider=ContextProvider(),
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
		log_handler=None
	)
	VCSBot.run(os.getenv("DISCORD_API_TOKEN"))

if __name__ == "__main__":
	runForPoetry()