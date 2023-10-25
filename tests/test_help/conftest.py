import asyncio
import pathlib
import sys
from typing import AsyncGenerator, Generator

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands

from bot.help import BotHelpCommand  # flake8: noqa: I005
from bot.main import BotConstructor  # flake8: noqa: I005

# flake8: noqa: I005

@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit() -> commands.Bot:
	intents = discord.Intents.all()
	VCSBot = BotConstructor(
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

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> AsyncGenerator[None, None]:
	yield
	await dpytest.empty_queue()