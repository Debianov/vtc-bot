from typing import Type

import pytest
from discord.ext import commands

from bot.data import ChannelGroup, DiscordObjectGroup, UserGroup


@pytest.mark.parametrize(
	"check_class",
	[
		UserGroup, ChannelGroup
	]
)
def test_main_discord_object_group(
	discordContext: commands.Context,
	check_class: Type[DiscordObjectGroup]
):
	a = check_class(discordContext)
	assert a.ctx == discordContext

@pytest.mark.parametrize(
	"check_class, user_identif",
	[
		(UserGroup, "usr"),
		(ChannelGroup, "ch")
	]
)
def test_equal_discord_object_group(
	discordContext: commands.Context,
	check_class: Type[DiscordObjectGroup],
	user_identif: str
):
	a = check_class(discordContext)
	assert a == user_identif