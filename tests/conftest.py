import asyncio
import pathlib
import sys
from typing import Any, AsyncGenerator, Dict, Generator, Iterable

import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
import psycopg
import pytest
import pytest_asyncio

from bot.exceptions import StartupBotError
from bot.help import BotHelpCommand
from bot.main import BotConstructor, DBConnFactory, _setup_i18n
from bot.utils import (
	ContextProvider,
	DelayedExpressionReplacer,
	MockLocator,
	getEnvIfExist,
	isIterable
)

root = pathlib.Path.cwd()

sys.path.append(str(root))

from bot.utils import Case

# flake8: noqa: I005
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="package")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> AsyncGenerator[None, None]:
	yield
	await dpytest.empty_queue()

def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> None:
	"""
	 The `pytest.mark.doDelayedExpression` implementation.
	 Iter all args that passing to a test function, find and executed all
	 `delayedExpression`s. The results of execution are writed in the same
	 place (`DelayedExpressionReplacer` for more info).
	 If object isn't iterable it is passed.
	"""
	if pyfuncitem.get_closest_marker("doDelayedExpression"):
		params_from_func = pyfuncitem.callspec.params
		params_and_fixtures = pyfuncitem.funcargs
		params_with_iterables = filterIterableParameters(params_from_func)
		fixtures = filterFixtures(params_and_fixtures, params_with_iterables)
		for _, iterable in params_with_iterables.items():
			DelayedExpressionReplacer(
				iterable,
				fixtures
			).go()

def filterIterableParameters(
	params_from_func: Dict[str, Any]
) -> Dict[str, Iterable]:
	params_with_case: Dict[str, Iterable] = {}
	for (param, instance) in params_from_func.items():
		if isIterable(instance):
			params_with_case[param] = instance
		else:
			print("filterIterableParameters", "The object is not iterable. "
			"Skipped to checking by fixture.")
	return params_with_case


def filterFixtures(
	params_and_fixtures: Dict[str, Any],
	params_with_iterables: Dict[str, Iterable]
) -> Dict[str, Any]:
	fixtures: Dict[str, Case] = params_and_fixtures.copy()
	for param_key in params_with_iterables.keys():
		fixtures.pop(param_key)
	return fixtures

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="package", autouse=True, name="db")
async def setupDB() -> psycopg.AsyncConnection[Any]:
	if github_action_envs := getEnvIfExist(
		"POSTGRES_HOST",
		"POSTGRES_PORT",
		"POSTGRES_DB",
		"POSTGRES_USER"
	):
		future_dbconn = await DBConnFactory(
			host=github_action_envs[0],
			port=github_action_envs[1],
			dbname=github_action_envs[2],
			user=github_action_envs[3]
		)
	elif envs := getEnvIfExist(
		"POSTGRES_DB",
		"POSTGRES_USER"
	):
		future_dbconn = await DBConnFactory(
			dbname=envs[0],
			user=envs[1]
		)
	else:
		raise StartupBotError("Failed to extract environment variables.")
	return future_dbconn

@pytest.mark.asyncio
@pytest_asyncio.fixture(scope="function", autouse=True)
async def deleteTablesRecords(db: psycopg.AsyncConnection[Any]) -> AsyncGenerator[None, None]:
	async with db.cursor() as acur:
		yield
		await acur.execute(
			"""
			DELETE FROM log_targets;
			DELETE FROM guilds;
			"""
		)

@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit(db: psycopg.AsyncConnection[Any]) -> commands.Bot:
	intents = discord.Intents.all()
	i18n_translator = _setup_i18n(db)
	VCSBot = BotConstructor(
		dbconn=db,
		context_provider=ContextProvider(),
		command_prefix="",
		intents=intents,
		help_command=BotHelpCommand(),
		load_cogs=False,
		i18n_translator=i18n_translator
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

@pytest_asyncio.fixture(scope="package", autouse=True, name="discordContext")
async def createDiscordContext(bot: commands.Bot) -> commands.Context:
	message = await dpytest.message("help")
	dpytest.get_message()
	current_ctx = await bot.get_context(message)
	return current_ctx
