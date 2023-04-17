from discord.ext import commands
import discord.ext.test as dpytest
import discord
import sys
import pathlib
import pytest
import pytest_asyncio
from typing import Final, Union, Iterable, Optional, Callable, Type

root = pathlib.Path.cwd()

sys.path.append(str(root))
sys.path.append(str(root) + "/bot")

from bot.main import bot, initDB

pytest_plugins = ('pytest_asyncio',)

@pytest_asyncio.fixture
async def botInit() -> None:
	await bot.setup_hook()
	await bot._async_setup_hook()
	dpytest.configure(bot)
	return bot

@pytest_asyncio.fixture(autouse=True)
async def cleanUp() -> None:
	yield
	await dpytest.empty_queue()

def pytest_configure():
	pytest.global_prefix: Final = "sudo"
	pytest.access_prefix: Final = ""