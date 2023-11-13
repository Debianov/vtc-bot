
import discord
import discord.ext.test as dpytest
import pytest_asyncio
from discord.ext import commands

from bot.help import BotHelpCommand
from bot.main import BotConstructor
from bot.utils import ContextProvider


@pytest_asyncio.fixture(scope="package", autouse=True, name="bot")
async def botInit() -> commands.Bot:
	intents = discord.Intents.all()
	VCSBot = BotConstructor(
		context_provider=ContextProvider(),
		command_prefix="sudo ",
		intents=intents,
		help_command=BotHelpCommand(),
	)
	await VCSBot._async_setup_hook()
	await VCSBot.prepare()
	dpytest.configure(VCSBot, num_members=6)
	return VCSBot

@pytest_asyncio.fixture(scope="package", autouse=True, name="discordContext")
async def createDiscordContext(bot: commands.Bot) -> commands.Context:
	message = await dpytest.message("sudo help")
	current_ctx = await bot.get_context(message)
	return current_ctx