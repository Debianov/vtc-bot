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

from .help import BotHelpCommand

intents = discord.Intents.all()
class DBConnector:

	def __init__(
		self,	
		dbname: str,
		dbuser: str
	) -> None:
		self.dbname = dbname
		self.dbuser = dbuser

	async def initConnection(self) -> None:
		"""
		Функция для инициализации подключения к БД.
		"""
		self.dbconn = await psycopg.AsyncConnection.connect(f"dbname={self.dbname} user={self.dbuser}", autocommit=True)

	def getDBconn(self) -> psycopg.AsyncConnection[Any]:
		return self.dbconn

class BotConstructor(commands.Bot):

	def __init__(
			self,
			dbconn_instance: DBConnector,
			*args: Any,
			**kwargs: Any
		):
		self.dbconn_instance = dbconn_instance
		self.dbconn = None
		super().__init__(*args, **kwargs)

	def run(self, *args: Any, **kwargs: Any) -> None:
		current_loop = asyncio.get_event_loop()
		current_loop.run_until_complete(self.prepare())
		super().run(*args, **kwargs)

	async def prepare(self) -> None:
		await self.initDBConn()
		await self.initDBService()
		await self.initCogs()

	async def initDBConn(self) -> None:
		await self.dbconn_instance.initConnection()
		self.dbconn = self.dbconn_instance.getDBconn()

	async def initDBService(self) -> None:
		class DiscordObjectsDumper(psycopg.adapt.Dumper):
			"""
			Преобразовывает Discord-объекты в ID для записи в БД.
			"""

			def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> bytes:
				if isinstance(elem, commands.Context):
					return str(elem.guild.id).encode()
				return str(elem.id).encode()
		class DiscordObjectsLoader(psycopg.adapt.Loader):
			"""
			Преобразовывает записи из БД в объекты Discord.
			"""

			ctx = None

			def load(self, data: bytes) -> Union[discord.abc.Messageable, discord.abc.Connectable, str]: 
				string_data: str = data.decode()
				for attr in ('get_member', 'get_user', 'get_channel'):
					try:
						result: Optional[discord.abc.Messageable] = getattr(
							self.ctx, attr)(int(string_data))
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

def runForPoetry() -> None:
	with open("db_secret.sec") as file:
		dbconn_instance = DBConnector(file.readline(), file.readline())
	VCSBot = BotConstructor(
		dbconn_instance=dbconn_instance,
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
	)
	with open("dsAPI_secret.sec") as file:
		VCSBot.run(file.readline())

if __name__ == "__main__":
	runForPoetry()