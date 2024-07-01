from typing import List, Type

import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup
from bot.exceptions import SearchExpressionNotFound


@pytest.mark.parametrize(
	"group_identif, compare_data_group",
	[
		("usr", [UserGroup]),
		("ch", [ChannelGroup]),
		("ch+usr", [ChannelGroup, UserGroup]),
		("usr+ch", [UserGroup, ChannelGroup])
	]
)
@pytest.mark.asyncio
async def test_good_extractDataGroup(
	discordContext: commands.Context,
	group_identif: str,
	compare_data_group: List[Type[DiscordObjectsGroup]]
) -> None:
	a = SearchExpression()
	a.ctx = discordContext
	a.group_identif = group_identif
	a._extractDataGroup()
	for ind in range(0, len(a.data_groups)):
		assert isinstance(a.data_groups[ind], compare_data_group[ind])

@pytest.mark.parametrize(
	"group_identif",
	[
		"grp",
		"usrg",
		"wertch:*",
		"grp:*",
		"werwchesdf"
	]
)
@pytest.mark.asyncio
async def test_bad_extractDataGroup(
	discordContext: commands.Context,
	group_identif: str,
) -> None:
	a = SearchExpression()
	a.ctx = discordContext
	a.argument = group_identif
	a.group_identif = group_identif
	with pytest.raises(SearchExpressionNotFound):
		a._extractDataGroup()