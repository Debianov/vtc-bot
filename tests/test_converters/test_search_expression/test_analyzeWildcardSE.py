from typing import List, Type, Union

import discord
import pytest
from discord.ext import commands

from bot.converters import SearchExpression
from bot.data import ChannelGroup, DiscordObjectsGroup, UserGroup
from bot.exceptions import SearchExpressionNotFound
from bot.utils import createDiscordObjectsGroupInstance


@pytest.mark.parametrize(
	"wildcard, compare_data_groups",
	[
		("*", [UserGroup]),
		("*", [ChannelGroup]),
		("*", [ChannelGroup, UserGroup])
	]
)
@pytest.mark.asyncio
async def test_good_analyzeWildcard_with_one_group(
	discordContext: commands.Context,
	wildcard: str,
	compare_data_groups: List[Type[DiscordObjectsGroup]]
) -> None:
	compare_data_groups_instance = createDiscordObjectsGroupInstance(
		compare_data_groups,
		discordContext
	)
	a = SearchExpression()
	a.ctx = discordContext
	a.wildcard = wildcard
	a.result = []
	a.data_groups = compare_data_groups_instance
	a._analyzeWildcard()
	result_to_compare: List[
		Union[discord.abc.GuildChannel, discord.abc.Member]
	] = []
	for compare_data_group_instance in compare_data_groups_instance:
		result_to_compare += compare_data_group_instance.extractData()
	assert a.result == result_to_compare

@pytest.mark.parametrize(
	"wildcard",
	[
		("ewrwerwe"),
		("+"),
		("-"),
		("^"),
		("usr:*"),
	]
)
@pytest.mark.asyncio
async def test_bad_analyzeWildcard_with_all_groups(
	wildcard: str,
) -> None:
	a = SearchExpression()
	a.wildcard = wildcard
	a.argument = wildcard
	with pytest.raises(SearchExpressionNotFound):
		a._analyzeWildcard()