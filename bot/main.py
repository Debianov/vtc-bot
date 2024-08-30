"""
The main module that collects all the modules and starting the bot.
"""

import asyncio
import logging
import logging.config
import logging.handlers
import os
from typing import Any, Dict, Optional, Union

import discord
import psycopg
import yaml
from discord.ext import commands

from ._types import IDObjects
from .exceptions import StartupBotError
from .help import BotHelpCommand
from .mock import Mock, MockAsyncConnection
from .utils import ContextProvider, Language, Translator, getEnvIfExist


def _setup_logging(
	path: str = "bot/log-config.yaml"
) -> None:
	"""
	Parses .yaml config file and sets up loggers based on it.
	"""
	if os.path.exists(path):
		with open(path, "rt") as f:
			config = yaml.safe_load(f.read())
		logging.config.dictConfig(config)
	else:
		raise Exception(f".yaml config on {path} doesn't exist.")

def _setup_i18n(
	dbconn: psycopg.AsyncConnection[Any],
	path_to_locale: str = "locale"
) -> Translator:
	supported_languages = [Language("en", "english"), Language("ru", "russian")]
	translator = Translator("vtc-bot", path_to_locale,
							supported_languages, dbconn)
	logging.info("i18n successfully inits.")
	return translator

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
		i18n_translator: Translator,
		dbconn: psycopg.AsyncConnection[Any] = MockAsyncConnection(),
		context_provider: ContextProvider = ContextProvider(),
		cog_load: bool = True,
		*args: Any,
		**kwargs: Any
	) -> None:
		self.i18n_translator = i18n_translator
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
		translator = self.i18n_translator

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

		class LanguageObjectsDumper(psycopg.adapt.Dumper):
			"""
			This adapter converts `utils.Language` to a str in the PostgresSQL database.
			"""

			def dump(
				self,
				elem: Language
			) -> bytes:
				return elem.getShortName().encode()

		class LanguageObjectsLoader(psycopg.adapt.Loader):
			"""
			This adapter converts str to `utils.Language`.
			"""

			def load(
				self,
				data: bytes
			) -> Language | str:
				string_data: str = data.decode()
				return (
					translator.getSupportedLanguageByShortName(string_data) or
					string_data
				)

		self.dbconn.adapters.register_dumper(  # type: ignore [union-attr]
			discord.abc.Messageable, DiscordObjectsDumper)
		self.dbconn.adapters.register_loader("bigint[]", # type: ignore [union-attr]
			DiscordObjectsLoader)
		self.dbconn.adapters.register_dumper(  # type: ignore [union-attr]
			Language, LanguageObjectsDumper)
		self.dbconn.adapters.register_loader("text", # type: ignore [union-attr]
			LanguageObjectsLoader)

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
	_setup_logging()
	loop = asyncio.get_event_loop()
	if extract_envs := getEnvIfExist("POSTGRES_DB", "POSTGRES_USER"):
		dbconn = loop.run_until_complete(DBConnFactory(
			dbname=extract_envs[0],
			user=extract_envs[1]
		))
	else:
		raise StartupBotError(
			"Failed to extract environment variables.")
	intents = discord.Intents.all()
	intents.dm_messages = False
	i18n_translator = _setup_i18n(dbconn)
	VCSBot = BotConstructor(
		command_prefix="",
		dbconn=dbconn,
		context_provider=ContextProvider(),
		intents=intents,
		help_command=BotHelpCommand(),
		log_handler=None,
		i18n_translator=i18n_translator
	)
	VCSBot.run(os.getenv("DISCORD_API_TOKEN"))

if __name__ == "__main__":
	runForPoetry()