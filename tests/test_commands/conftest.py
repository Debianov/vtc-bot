import os
import pathlib
import sys
from typing import Any, Optional

import discord
import discord.ext.test as dpytest
import psycopg
import pytest
import pytest_asyncio
from discord.ext import commands

from bot.help import BotHelpCommand
from bot.main import BotConstructor, DBConnFactory
from bot.utils import ContextProvider

root = pathlib.Path.cwd()
sys.path.append(str(root))

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", autouse=True, name="db")
async def setupDB() -> Optional[psycopg.AsyncConnection[Any]]:
	future_dbconn = await DBConnFactory(
		host=os.getenv("POSTGRES_HOST"),
		port=os.getenv("POSTGRES_PORT"),
		password=os.getenv("POSTGRES_PASSWORD"),
		dbname=os.getenv("POSTGRES_TEST_DBNAME"),
		user=os.getenv("POSTGRES_USER")
	)
	return future_dbconn

@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit(db: Optional[psycopg.AsyncConnection[Any]]) -> commands.Bot:
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
	config = dpytest.get_config()
	pytest.test_guild = config.guilds[0]
	pytest.test_channel = config.channels[0]
	for (ind, member) in enumerate(config.members):
		setattr(pytest, f"test_member{ind}", member)
	return VCSBot

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