import discord
import pytest
import pytest_asyncio
import psycopg
import asyncio
from typing import Optional, Any

from bot.main import DBConnector, BotConstructor, DBConnFactory
from bot.help import BotHelpCommand

@pytest.fixture(scope="package")
def event_loop() -> None:
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", name="db")
async def setupDB() -> Optional[psycopg.AsyncConnection[Any]]:
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
	return dbconn

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", autouse=True)
async def createTargetTable(db) -> None:
	async with db.cursor() as acur:
		await acur.execute(
			"""CREATE TABLE public.target (
			id bigint,
			context_id bigint,
			target bigint[],
			act text,
			d_in bigint[],
			name text,
			priority integer,
			output text,
			other text
			);"""
		)
		yield
		await acur.execute(
			"""
			DROP TABLE target;
			"""
		)

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="function", autouse=True)
async def deleteTargetTable(db) -> None:
	yield
	async with db.cursor() as acur:
		await acur.execute(
			"DELETE FROM target;"
		)