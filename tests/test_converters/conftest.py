import pathlib
import sys
from typing import Any, AsyncGenerator, Optional

import discord
import discord.ext.test as dpytest
import psycopg
import pytest
import pytest_asyncio
from discord.ext import commands

from bot.exceptions import StartupBotError
from bot.help import BotHelpCommand
from bot.main import BotConstructor, DBConnFactory
from bot.utils import (
	ContextProvider,
	DiscordObjEvaluator,
	MockLocator,
	getEnvIfExist
)

@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit() -> commands.Bot:
	intents = discord.Intents.all()
	VCSBot = BotConstructor(
		context_provider=ContextProvider(),
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
		load_cogs=False,
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

@pytest.fixture(scope="package", autouse=True, name="discordObjectEvaluator")
def initEvaluator(mockLocator: MockLocator) -> DiscordObjEvaluator:
	instance = DiscordObjEvaluator(mockLocator)
	return instance