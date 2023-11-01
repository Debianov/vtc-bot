import asyncio
import pathlib
import sys
from typing import AsyncGenerator, Generator

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands

root = pathlib.Path.cwd()

sys.path.append(str(root))

from bot.help import BotHelpCommand  # flake8: noqa: I005
from bot.main import BotConstructor  # flake8: noqa: I005

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