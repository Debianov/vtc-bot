from typing import AsyncGenerator

import discord
import discord.ext.test as dpytest
import pytest_asyncio
from discord.ext import commands

from bot.help import BotHelpCommand
from bot.main import BotConstructor


@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit() -> commands.Bot:
	intents = discord.Intents.all()
	VCSBot = BotConstructor(
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
		cog_load=False
	)
	await VCSBot._async_setup_hook()
	await VCSBot.prepare()
	dpytest.configure(VCSBot, num_members=6)
	return VCSBot

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> AsyncGenerator[None, None]:
	yield
	await dpytest.empty_queue()