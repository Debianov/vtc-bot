
import pytest
from discord.ext import commands

from bot.data import DiscordObjectsGroup


def test_main_discord_object_group(discordContext: commands.Context):
	a = DiscordObjectsGroup(discordContext)
	assert a.ctx == discordContext

def test_equal_discord_object_group(discordContext: commands.Context):
	a = DiscordObjectsGroup(discordContext)
	assert a == ""

def test_extractData_discord_object_group(discordContext: commands.Context):
	a = DiscordObjectsGroup(discordContext)
	with pytest.raises(NotImplementedError):
		a.extractData()