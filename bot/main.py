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
			dbconn: psycopg.AsyncConnection[Any] = None,
			*args: Any,
			**kwargs: Any
		):
		self.dbconn = dbconn
		super().__init__(*args, **kwargs)

	def run(self, *args: Any, **kwargs: Any) -> None:
		current_loop = asyncio.get_event_loop()
		current_loop.run_until_complete(self.prepare())
		super().run(*args, **kwargs)

	async def prepare(self) -> None:
		if self.dbconn:
			await self.initDBService()
		await self.initCogs()

	async def initDBService(self) -> None:

		class DiscordObjectsDumper(psycopg.adapt.Dumper):
			"""
			Преобразовывает Discord-объекты в ID для записи в БД.
			"""
			def dump(self, elem: Union[discord.abc.Messageable, discord.abc.Connectable]) -> bytes:
				return str(elem.id).encode()
				
		self.dbconn.adapters.register_dumper(discord.abc.Messageable, DiscordObjectsDumper)

	async def initCogs(self) -> None:
		for module_name in ("commands",):
			await self.load_extension(f"bot.{module_name}")
		for cog_name in self.cogs:
			cog = self.get_cog(cog_name)
			cog.dbconn = self.dbconn

async def DBConnFactory(*args: Any, **kwargs: Any) -> psycopg.AsyncConnection[Any]:
	dbconn_instance = DBConnector(*args, **kwargs)
	await dbconn_instance.initConnection()
	return dbconn_instance.getDBconn()

def runForPoetry() -> None:
	loop = asyncio.get_event_loop()
	with open("db_secret.sec") as file:
		dbconn = loop.run_until_complete(DBConnFactory(dbname=file.readline(), dbuser=file.readline()))
	intents = discord.Intents.all()
	VCSBot = BotConstructor(
		dbconn=dbconn,
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
	)
	with open("dsAPI_secret.sec") as file:
		VCSBot.run(file.readline())

if __name__ == "__main__":
	runForPoetry()