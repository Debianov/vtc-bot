from discord.ext import commands
import discord.ext.test as dpytest
import discord
import sys
import asyncio
import pathlib
import pytest
import pytest_asyncio
import psycopg
from typing import Final, Union, Iterable, Optional, Callable, Type, Any

root = pathlib.Path.cwd()

sys.path.append(str(root))
sys.path.append(str(root) + "/bot")

from bot.main import bot, initDB

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="package")
def event_loop() -> None:
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()

@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit() -> commands.Bot:
	await bot._async_setup_hook()
	dpytest.configure(bot, num_members=6)
	config = dpytest.get_config()
	pytest.test_guild = config.guilds[0]
	pytest.test_channel = config.channels[0]
	for (ind, member) in enumerate(config.members):
		setattr(pytest, f"test_member{ind}", member)
	return bot

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> None:
	yield
	await dpytest.empty_queue()

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="module", name="db")
async def setupDB() -> Optional[psycopg.AsyncConnection[Any]]:
	with open("test_db_secret.sec") as text:
		aconn = await initDB(text.readline(), text.readline())
		return aconn

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="module", autouse=True)
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