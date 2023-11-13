from typing import List, Type

import pytest
from discord.ext import commands

from bot.data import (
	ChannelGroup,
	DataGroupAnalyzator,
	DiscordObjectsGroup,
	UserGroup
)


@pytest.mark.parametrize(
	"group_identif",
	[
		"usr+ch", "ch", "usr"
	]
)
def test_main(discordContext: commands.Context, group_identif: str):
	instance = DataGroupAnalyzator(discordContext, group_identif)
	assert instance.split_string == group_identif.split("+")
	assert instance.relevant_groups == []
	assert instance.ctx == discordContext

@pytest.mark.parametrize(
	"group_identif, compare_relevant_groups",
	[
		("usr+ch", [UserGroup, ChannelGroup]),
		("ch", [ChannelGroup]),
		("usr", [UserGroup])
	]
)
def test_good_analyze(
	discordContext: commands.Context,
	group_identif: str,
	compare_relevant_groups: List[Type[DiscordObjectsGroup]]
	) -> None:
	instance = DataGroupAnalyzator(discordContext, group_identif)
	compare_relevenat_groups_instance: List[DiscordObjectsGroup] = []
	for relevant_group in compare_relevant_groups:
		compare_relevenat_groups_instance.append(relevant_group(discordContext))
	instance.analyze()
	assert instance.relevant_groups == compare_relevenat_groups_instance