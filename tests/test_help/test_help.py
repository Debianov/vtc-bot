import discord.ext.test as dpytest
import pytest
from discord.ext import commands

from bot.embeds import BotEmbed


@pytest.mark.asyncio
async def test_main_help_page() -> None:
	await dpytest.message("sudo help")
	assert dpytest.verify().message()

@pytest.mark.asyncio
async def test_commands_help_page(bot: commands.Bot) -> None:
	for command in bot.walk_commands():
		await dpytest.message(f"sudo help {command.qualified_name}")
		assert dpytest.verify().message()

@pytest.mark.parametrize(
	"command_arg",
	[
		("dfsdf"),
		("log dsfsdfsd")
	]
)
@pytest.mark.asyncio
async def test_bad_commands_help_page(
	command_arg: str
) -> None:
	await dpytest.message(f"sudo help {command_arg}")
	check_embed = BotEmbed(title="Документация")
	check_embed.add_field(
		name="Ошибка",
		value="Указанная команда не найдена."
	)
	assert dpytest.verify().message().embed(check_embed)