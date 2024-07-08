import pathlib
import sys
from typing import Any, AsyncGenerator

import discord
import discord.ext.test as dpytest
import psycopg
import pytest
import pytest_asyncio
from discord.ext import commands

from bot.exceptions import StartupBotError
from bot.help import BotHelpCommand
from bot.main import BotConstructor, DBConnFactory
from bot.utils import ContextProvider, MockLocator, getEnvIfExist

root = pathlib.Path.cwd()
sys.path.append(str(root))

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", autouse=True, name="db")
async def setupDB() -> psycopg.AsyncConnection[Any]:
	if github_action_envs := getEnvIfExist(
		"POSTGRES_HOST",
		"POSTGRES_PORT",
		"POSTGRES_PASSWORD",
		"POSTGRES_TEST_DBNAME",
		"POSTGRES_USER"
	):
		future_dbconn = await DBConnFactory(
			host=github_action_envs[0],
			port=github_action_envs[1],
			password=github_action_envs[2],
			dbname=github_action_envs[3],
			user=github_action_envs[4]
		)
	elif envs := getEnvIfExist(
		"POSTGRES_TEST_DBNAME",
		"POSTGRES_USER"
	):
		future_dbconn = await DBConnFactory(
			dbname=envs[0],
			user=envs[1]
		)
	else:
		raise StartupBotError("Не удалось извлечь переменные окружения.")
	return future_dbconn

@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit(db: psycopg.AsyncConnection[Any]) -> commands.Bot:
	intents = discord.Intents.all()
	VCSBot = BotConstructor(
		dbconn=db,
		context_provider=ContextProvider(),
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
	)
	await VCSBot._async_setup_hook()
	await VCSBot.prepare()
	dpytest.configure(VCSBot, num_members=6)
	return VCSBot

@pytest.fixture(scope="package", autouse=True, name="mockLocator")
def initLocator() -> MockLocator:
	config = dpytest.get_config()
	locator = MockLocator(
		guild=config.guilds[0],
		channel=config.channels[0],
		members=list(config.guilds[0].members)
	)
	return locator

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", autouse=True)
async def createTargetTable(db) -> AsyncGenerator[None, None]:
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
async def deleteTargetTable(db) -> AsyncGenerator[None, None]:
	yield
	async with db.cursor() as acur:
		await acur.execute(
			"DELETE FROM target;"
		)