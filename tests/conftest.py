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
	dpytest.configure(bot)
	state_user = dpytest.backend.get_state().user
	bot.test_guild = dpytest.backend.make_guild(name="Test")
	author_from_bot = dpytest.backend.make_member(state_user, bot.test_guild)
	bot.test_channel = dpytest.backend.make_text_channel(guild=bot.test_guild, name="Test")
	bot.test_member0 = dpytest.backend.make_member(dpytest.backend.make_user("Test0", 2,
	id_num=386420570449051640), bot.test_guild)
	bot.test_member1 = dpytest.backend.make_member(dpytest.backend.make_user("Test1", 2,
	id_num=386420570449051641), bot.test_guild)
	bot.test_member2 = dpytest.backend.make_member(dpytest.backend.make_user("Test2", 2,
	id_num=386420570449051642), bot.test_guild)
	bot.test_member3 = dpytest.backend.make_member(dpytest.backend.make_user("Test3", 2,
	id_num=386420570449051643), bot.test_guild)
	return bot

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> None:
	yield
	await dpytest.empty_queue()

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="module")
async def setupDB() -> Optional[psycopg.AsyncConnection[Any]]: # TODO alias
	with open("test_db_secret.sec") as text:
		aconn = await initDB(text.readline(), text.readline())
		return aconn

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="module", autouse=True)
async def createTargetTable(setupDB) -> None:
	async with setupDB.cursor() as acur:
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
async def deleteTargetTable(setupDB) -> None:
	yield
	async with setupDB.cursor() as acur:
		await acur.execute(
			"DELETE FROM target;"
		)