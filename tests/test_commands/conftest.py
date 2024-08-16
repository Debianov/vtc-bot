import pathlib
import sys
from typing import Any

import discord
import discord.ext.test as dpytest
import psycopg
import pytest
import pytest_asyncio
from discord.ext import commands

from bot.help import BotHelpCommand
from bot.main import BotConstructor, _setup_i18n
from bot.utils import ContextProvider, MockLocator

root = pathlib.Path.cwd()
sys.path.append(str(root))


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