from typing import Type

import pytest
from discord.ext import commands

from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup


@pytest.mark.parametrize(
	"check_class",
	[
		DiscordObjectsGroup, UserGroup, ChannelGroup
	]
)
def test_main_discord_object_group(
	discordContext: commands.Context,
	check_class: Type[DiscordObjectsGroup]
):
	a = check_class(discordContext)
	assert a.ctx == discordContext

@pytest.mark.parametrize(
	"check_class, user_identif",
	[
		(DiscordObjectsGroup, ""),
		(UserGroup, "usr"),
		(ChannelGroup, "ch")
	]
)
def test_equal_discord_object_group(
	discordContext: commands.Context,
	check_class: Type[DiscordObjectsGroup],
	user_identif: str
):
	a = check_class(discordContext)
	assert a == user_identif

def test_extractData_discord_object_group(
	discordContext: commands.Context,
):
	a = DiscordObjectsGroup(discordContext)
	with pytest.raises(NotImplementedError):
		a.extractData()